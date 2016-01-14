package ch.unine.iiun.safecloud;


public interface EncoderDecoder {
    /**
     * Encode data.
     *
     * @param data Data to encode
     * @return Encoded data
     */
    public byte[] encode(final byte[] data);

    /**
     * Decoded data
     *
     * @param data Data to decoded
     * @return Decoded data
     */
    public byte[] decode(final byte[] data);
}
