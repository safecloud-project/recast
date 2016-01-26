package ch.unine.iiun.safecloud;

import org.springframework.stereotype.Service;

/**
 * An encoder/decoder that replies with the same data it receives.
 */
@Service(value = "bypass")
public class ByPassEncoderDecoder implements EncoderDecoder {

    @Override
    public byte[] encode(byte[] data) {
        return data;
    }

    @Override
    public byte[] decode(byte[] data) {
        return data;
    }
}
