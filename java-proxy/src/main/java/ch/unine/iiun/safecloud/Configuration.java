package ch.unine.iiun.safecloud;

import redis.clients.jedis.JedisPoolConfig;

public class Configuration {
    public static final Configuration INSTANCE = new Configuration();

    public JedisPoolConfig getJedisConfig() {
        JedisPoolConfig config = new JedisPoolConfig();
        config.setMaxTotal(1000);
        config.setBlockWhenExhausted(false);
        return config;
    }
}
