package ch.unine.iiun.safecloud;

import com.google.protobuf.ByteString;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;

import java.io.IOException;
import java.util.Comparator;
import java.util.List;
import java.util.Set;
import java.util.TreeSet;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

@Service
public class RedisStore implements Store {

    private static String redisHost = System.getenv("REDIS_PORT_6379_TCP_ADDR") != null ? System.getenv("REDIS_PORT_6379_TCP_ADDR") : "127.0.0.1";
    private static int redisPort = System.getenv("REDIS_PORT_6379_TCP_ADDR") != null ? Integer.parseInt(System.getenv("REDIS_PORT_6379_TCP_PORT")) : 6379;


    static JedisPool POOL = new JedisPool(Configuration.INSTANCE.getJedisConfig(), redisHost, redisPort);

    @Autowired(required = true)
    private ErasureClient erasure;

    @Autowired(required = true)
    private ByPassEncoderDecoder bypass;

    public byte[] get(final String path) throws MissingResourceException, IOException {
        if (path == null) {
            throw new IllegalArgumentException("path argument cannot be null");
        }
        if (path.isEmpty()) {
            throw new IllegalArgumentException("path argument cannot be empty");
        }
        byte[] raw;
        try (Jedis redis = POOL.getResource()) {
            final String baseKey = path + "-*";
            Set<String> keys = new TreeSet<>(new StripKeyComparator());
            keys.addAll(redis.keys(baseKey));
            if (keys.isEmpty()) {
                throw new MissingResourceException("not found");
            }
            byte[][] keysAsArray = new byte[keys.size()][];
            int i = 0;
            for (String key : keys) {
                keysAsArray[i] = key.getBytes();
                i++;
            }
            List<Playcloud.Strip> strips = redis.mget(keysAsArray).stream().filter(result -> result != null).map(data -> Playcloud.Strip.newBuilder().setData(ByteString.copyFrom(data)).build()).collect(Collectors.toList());
            return this.getEncoderDecoder().decode(strips);
        }
    }

    public String put(final String path, final byte[] data) throws IOException {
        if (path == null) {
            throw new IllegalArgumentException("path argument cannot be null");
        }
        if (path.isEmpty()) {
            throw new IllegalArgumentException("path argument cannot be empty");
        }
        if (data == null) {
            throw new IllegalArgumentException("data argument cannot be null");
        }
        if (data.length == 0) {
            throw new IllegalArgumentException("data argument cannot be an empty array of data");
        }
        List<Playcloud.Strip> strips = this.getEncoderDecoder().encode(data);
        byte[][] dataToStore = new byte[2 * strips.size()][];
        for (int i = 0, j = 0; i < strips.size(); i++, j += 2) {
            byte[] stripKey = (path + "-" + i).getBytes();
            byte[] stripData = strips.get(i).getData().toByteArray();
            dataToStore[j] = stripKey;
            dataToStore[j + 1] = stripData;
        }
        try (Jedis redis = POOL.getResource()) {
            redis.mset(dataToStore);
        }
        return path;
    }

    public EncoderDecoder getEncoderDecoder() {
        final String ecType = System.getenv("EC_TYPE");
        if (ecType != null && ecType.trim().equalsIgnoreCase("bypass")) {
            return this.bypass;
        }
        return this.erasure;
    }

    public void setEncoderDecoder(final EncoderDecoder encoderDecoder) {
        if (encoderDecoder instanceof ByPassEncoderDecoder) {
            this.bypass = (ByPassEncoderDecoder) encoderDecoder;
        }
        else {
            this.erasure = (ErasureClient) encoderDecoder;
        }
    }

    public static class StripKeyComparator implements Comparator<String> {
        public static Pattern PATTERN = Pattern.compile("\\-(\\d+)$");

        @Override
        public int compare(String first, String second) {
            Matcher matcher = PATTERN.matcher(first);
            matcher.find();
            int firstIndex = Integer.parseInt(matcher.group(1));
            Matcher secondMatcher = PATTERN.matcher(second);
            secondMatcher.find();
            int secondIndex = Integer.parseInt(secondMatcher.group(1));
            return firstIndex - secondIndex;
        }
    }
}
