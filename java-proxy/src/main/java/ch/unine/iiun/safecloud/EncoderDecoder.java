package ch.unine.iiun.safecloud;


import java.util.List;

public interface EncoderDecoder {
    /**
     * Encode data.
     *
     * @param data Data to encode
     * @return Encoded data
     */
    public List<Playcloud.Strip> encode(final byte[] data);

    /**
     * Decoded data
     *
     * @param data Data to decoded
     * @return Decoded data
     */
    public byte[] decode(final byte[] data);
}
