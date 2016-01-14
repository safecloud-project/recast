package ch.unine.iiun.safecloud;

import java.io.IOException;

/**
 * An interface for data stores.
 */
public interface Store {
    /**
     * Retrieve data stored under a given key.
     *
     * @param key The key under which the data is stored
     * @return The data in an array of bytes
     * @throws MissingResourceException If no data can be found under the given key
     * @throws IOException              If an error occurs while communicating with the data store
     */
    public byte[] get(final String key) throws MissingResourceException, IOException;

    /**
     * Store data under a given key.
     *
     * @param key  The key that should be used to store the data
     * @param data The data to store
     * @return The key under which the data was stored. It should be the same as the given as a parameter.
     * @throws IOException If an error occurs while communicating with the data store
     */
    public String put(final String key, final byte[] data) throws IOException;
}
