package ch.unine.iiun.safecloud;

import org.junit.*;
import org.mockito.Mockito;
import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;

import java.io.IOException;

public class TestStore {

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

    private static class MockedErasureClient extends ErasureClient {

        public MockedErasureClient() throws IOException {
        }

        @Override
        public byte[] encode(byte[] data) {
            return data;
        }

        @Override
        public byte[] decode(byte[] data) {
            return data;
        }
    }

    private static JedisPool originalPool;

    @BeforeClass
    public static void setUp() {
        originalPool = Store.POOL;
        Store.POOL = Mockito.mock(JedisPool.class);
        Mockito.when(Store.POOL.getResource()).thenReturn(new MockedJedis());
    }

    @AfterClass
    public static void tearDown() {
        Store.POOL = originalPool;
    }


    @Test
    public void testGetNullPath() throws MissingResourceException, IOException {
        Store store = new Store();
        try {
            store.get(null);
            Assert.fail("Store.get should throw an exception when receiving a null path");
        } catch (IllegalArgumentException e) {
            Assert.assertEquals(e.getMessage(), "path argument cannot be null");
        }
    }

    @Test
    public void testGetEmptyPath() throws MissingResourceException, IOException {
        Store store = new Store();
        try {
            store.get("");
            Assert.fail("Store.get should throw an exception when receiving an empty path");
        } catch (IllegalArgumentException e) {
            Assert.assertEquals(e.getMessage(), "path argument cannot be empty");
        }
    }


    @Test
    public void testGetNonExistingPath() throws IOException, NoSuchMethodException {
        Store store = new Store();
        String path = "nonexistingpath";
        try {
            store.get(path);
            Assert.fail("Store.get should throw an exception if the path does not lead to any resource");
        } catch (MissingResourceException e) {
            Assert.assertEquals(e.getMessage(), "missing resource");
        }
    }

    @Test
    public void testPutNullPath() throws IOException {
        Store store = new Store();
        byte[] data = {1, 2, 3};
        try {
            store.put(null, data);
            Assert.fail("Store.put should throw an exception when receiving a null path");
        } catch (IllegalArgumentException e) {
            Assert.assertEquals(e.getMessage(), "path argument cannot be null");
        }
    }

    @Test
    public void testPutEmptyPath() throws MissingResourceException, IOException {
        Store store = new Store();
        byte[] data = {1, 2, 3};
        try {
            store.put("", data);
            Assert.fail("Store.put should throw an exception when receiving an empty path");
        } catch (IllegalArgumentException e) {
            Assert.assertEquals(e.getMessage(), "path argument cannot be empty");
        }
    }

    @Test
    public void testPutNullData() throws MissingResourceException, IOException {
        Store store = new Store();
        try {
            store.put("path", null);
            Assert.fail("Store.put should throw an exception when receiving null data");
        } catch (IllegalArgumentException e) {
            Assert.assertEquals(e.getMessage(), "data argument cannot be null");
        }
    }

    @Test
    public void testPutEmptyData() throws MissingResourceException, IOException {
        Store store = new Store();
        byte[] data = {};
        try {
            store.put("path", data);
            Assert.fail("Store.put should throw an exception when receiving an emtpy array of data");
        } catch (IllegalArgumentException e) {
            Assert.assertEquals(e.getMessage(), "data argument cannot be an empty array of data");
        }
    }

    @Test
    public void testPutNominal() throws MissingResourceException, IOException {
        Store store = new Store();
        store.setErasureClient(new MockedErasureClient());
        String path = "path";
        byte[] data = {1, 2, 3};
        String result = store.put(path, data);
        Assert.assertEquals(result, path);
    }

}
