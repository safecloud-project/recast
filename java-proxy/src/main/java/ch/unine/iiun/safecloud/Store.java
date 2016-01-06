package ch.unine.iiun.safecloud;

import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.JedisPoolConfig;

import java.io.IOException;

public class Store {

    static JedisPool POOL = new JedisPool(new JedisPoolConfig(), System.getenv("REDIS_PORT_6379_TCP_ADDR") != null ? System.getenv("REDIS_PORT_6379_TCP_ADDR") : "127.0.0.1");

    private ErasureClient erasureClient;

    public Store() throws IOException {
        this.erasureClient = new ErasureClient();
    }



    public byte[] get(String path) throws MissingResourceException, IOException {
        if (path == null) {
            throw new IllegalArgumentException("path argument cannot be null");
        }
        if (path.isEmpty()) {
            throw new IllegalArgumentException("path argument cannot be empty");
        }
        Jedis redis = POOL.getResource();
        byte[] raw = redis.get(path.getBytes());
        if (raw == null) {
            throw new MissingResourceException("missing resource");
        }
        byte [] data = this.erasureClient.decode(raw);
        return data;
    }

    public String put(String path, byte[] data) throws IOException {
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
        Jedis redis = POOL.getResource();
        byte[] encoded = this.erasureClient.encode(data);
        return redis.set(path.getBytes(), encoded);
    }

    public ErasureClient getErasureClient() {
        return erasureClient;
    }

    public void setErasureClient(ErasureClient erasureClient) {
        this.erasureClient = erasureClient;
    }
}
