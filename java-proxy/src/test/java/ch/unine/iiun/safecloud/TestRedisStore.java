package ch.unine.iiun.safecloud;

import org.junit.AfterClass;
import org.junit.Assert;
import org.junit.BeforeClass;
import org.junit.Test;
import org.mockito.Mockito;
import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;

import java.io.IOException;

public class TestRedisStore {

    private static class MockedJedis extends Jedis {
        @Override
        public byte[] get(byte[] key) {
            return null;
        }

        @Override
        public String set(byte[] key, byte[] value) {
            return new String(key);
        }
    }

    private static JedisPool originalPool;

    @BeforeClass
    public static void setUp() {
        originalPool = RedisStore.POOL;
        RedisStore.POOL = Mockito.mock(JedisPool.class);
        Mockito.when(RedisStore.POOL.getResource()).thenReturn(new MockedJedis());
    }

    @AfterClass
    public static void tearDown() {
        RedisStore.POOL = originalPool;
    }


    @Test
    public void testGetNullPath() throws MissingResourceException, IOException {
        RedisStore redisStore = new RedisStore();
        try {
            redisStore.get(null);
            Assert.fail("RedisStore.get should throw an exception when receiving a null path");
        } catch (IllegalArgumentException e) {
            Assert.assertEquals(e.getMessage(), "path argument cannot be null");
        }
    }

    @Test
    public void testGetEmptyPath() throws MissingResourceException, IOException {
        RedisStore redisStore = new RedisStore();
        try {
            redisStore.get("");
            Assert.fail("RedisStore.get should throw an exception when receiving an empty path");
        } catch (IllegalArgumentException e) {
            Assert.assertEquals(e.getMessage(), "path argument cannot be empty");
        }
    }


    @Test
    public void testGetNonExistingPath() throws IOException, NoSuchMethodException {
        RedisStore redisStore = new RedisStore();
        String path = "nonexistingpath";
        try {
            redisStore.get(path);
            Assert.fail("RedisStore.get should throw an exception if the path does not lead to any resource");
        } catch (MissingResourceException e) {
            Assert.assertEquals(e.getMessage(), "missing resource");
        }
    }

    @Test
    public void testPutNullPath() throws IOException {
        RedisStore redisStore = new RedisStore();
        byte[] data = {1, 2, 3};
        try {
            redisStore.put(null, data);
            Assert.fail("RedisStore.put should throw an exception when receiving a null path");
        } catch (IllegalArgumentException e) {
            Assert.assertEquals(e.getMessage(), "path argument cannot be null");
        }
    }

    @Test
    public void testPutEmptyPath() throws MissingResourceException, IOException {
        RedisStore redisStore = new RedisStore();
        byte[] data = {1, 2, 3};
        try {
            redisStore.put("", data);
            Assert.fail("RedisStore.put should throw an exception when receiving an empty path");
        } catch (IllegalArgumentException e) {
            Assert.assertEquals(e.getMessage(), "path argument cannot be empty");
        }
    }

    @Test
    public void testPutNullData() throws MissingResourceException, IOException {
        RedisStore redisStore = new RedisStore();
        try {
            redisStore.put("path", null);
            Assert.fail("RedisStore.put should throw an exception when receiving null data");
        } catch (IllegalArgumentException e) {
            Assert.assertEquals(e.getMessage(), "data argument cannot be null");
        }
    }

    @Test
    public void testPutEmptyData() throws MissingResourceException, IOException {
        RedisStore redisStore = new RedisStore();
        byte[] data = {};
        try {
            redisStore.put("path", data);
            Assert.fail("RedisStore.put should throw an exception when receiving an emtpy array of data");
        } catch (IllegalArgumentException e) {
            Assert.assertEquals(e.getMessage(), "data argument cannot be an empty array of data");
        }
    }

    @Test
    public void testPutNominal() throws MissingResourceException, IOException {
        RedisStore redisStore = new RedisStore();
        redisStore.setEncoderDecoder(new ByPassEncoderDecoder());
        String path = "path";
        byte[] data = {1, 2, 3};
        String result = redisStore.put(path, data);
        Assert.assertEquals(result, path);
    }

}
