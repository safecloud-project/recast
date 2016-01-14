package ch.unine.iiun.safecloud;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;

import java.io.IOException;

@Service
public class RedisStore implements Store {

    private static String redisHost = System.getenv("REDIS_PORT_6379_TCP_ADDR") != null ? System.getenv("REDIS_PORT_6379_TCP_ADDR") : "127.0.0.1";
    private static int redisPort = System.getenv("REDIS_PORT_6379_TCP_ADDR") != null ? Integer.parseInt(System.getenv("REDIS_PORT_6379_TCP_PORT")) : 6379;


    static JedisPool POOL = new JedisPool(Configuration.INSTANCE.getJedisConfig(), redisHost, redisPort);

    private EncoderDecoder encoderDecoder;


    public byte[] get(final String path) throws MissingResourceException, IOException {
        if (path == null) {
            throw new IllegalArgumentException("path argument cannot be null");
        }
        if (path.isEmpty()) {
            throw new IllegalArgumentException("path argument cannot be empty");
        }
        byte[] raw;
        try (Jedis redis = POOL.getResource()) {
            raw = redis.get(path.getBytes());
        }
        if (raw == null) {
            throw new MissingResourceException("missing resource");
        }
        byte[] data = this.encoderDecoder.decode(raw);
        return data;
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
        try (Jedis redis = POOL.getResource()) {
            byte[] encoded = this.encoderDecoder.encode(data);
            return redis.set(path.getBytes(), encoded);
        }

    }

    public EncoderDecoder getEncoderDecoder() {
        return encoderDecoder;
    }

    @Autowired
    public void setEncoderDecoder(final EncoderDecoder encoderDecoder) {
        this.encoderDecoder = encoderDecoder;
    }
}
