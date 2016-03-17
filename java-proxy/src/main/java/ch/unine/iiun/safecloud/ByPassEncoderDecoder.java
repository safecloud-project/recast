package ch.unine.iiun.safecloud;

import com.google.protobuf.ByteString;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

/**
 * An encoder/decoder that replies with the same data it receives.
 */
@Service(value = "bypass")
public class ByPassEncoderDecoder implements EncoderDecoder {
    public static final int K = 10;
    public static final int M = 4;

    @Override
    public List<Playcloud.Strip> encode(byte[] data) {
        List<Playcloud.Strip> strips = new ArrayList<>(ByPassEncoderDecoder.K);
        int stripLength = (int) Math.ceil(data.length / ByPassEncoderDecoder.K);
        for (int i = 0; i < data.length; i += stripLength) {
            Playcloud.Strip strip = Playcloud.Strip.newBuilder().setData(ByteString.copyFrom(data,i, stripLength)).build();
            strips.add(strip);
        }
        return strips;
    }

    @Override
    public byte[] decode(List<Playcloud.Strip> strips) {
        ByteString data = ByteString.EMPTY;
        for (Playcloud.Strip strip : strips) {
            data = data.concat(strip.getData());
        }
        return data.toByteArray();
    }
}
