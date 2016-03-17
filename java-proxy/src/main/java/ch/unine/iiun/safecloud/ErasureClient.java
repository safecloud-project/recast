package ch.unine.iiun.safecloud;

import com.google.protobuf.ByteString;
import io.grpc.internal.ManagedChannelImpl;
import io.grpc.netty.NegotiationType;
import io.grpc.netty.NettyChannelBuilder;
import org.springframework.context.annotation.Primary;
import org.springframework.stereotype.Service;

import java.util.List;

@Primary
@Service(value = "grpc")
public class ErasureClient implements EncoderDecoder {

    public static final String DEFAULT_HOST = (System.getenv("CODER_PORT_1234_TCP_ADDR") != null) ? System.getenv("CODER_PORT_1234_TCP_ADDR") : "127.0.0.1";
    public static final int DEFAULT_PORT = (System.getenv("CODER_PORT_1234_TCP_PORT") != null) ? Integer.parseInt(System.getenv("CODER_PORT_1234_TCP_PORT")) : 1234;


    private ManagedChannelImpl channel;
    private EncoderDecoderGrpc.EncoderDecoderBlockingStub blockingStub;

    private void setUp() {
        if (this.channel == null) {
            this.channel = NettyChannelBuilder.forAddress(DEFAULT_HOST, DEFAULT_PORT)
                    .negotiationType(NegotiationType.PLAINTEXT)
                    .build();
        }
        if (this.blockingStub == null) {
            this.blockingStub = EncoderDecoderGrpc.newBlockingStub(channel);
        }
    }

    public List<Playcloud.Strip> encode(final byte[] data) {
        setUp();
        ByteString payload = ByteString.copyFrom(data);
        Playcloud.EncodeRequest request = Playcloud.EncodeRequest.newBuilder().setPayload(payload).build();
        Playcloud.EncodeReply reply = blockingStub.encode(request);
        return reply.getStripsList();
    }

    public byte[] decode(final List<Playcloud.Strip> strips) {
        setUp();
        Playcloud.DecodeRequest request = Playcloud.DecodeRequest.newBuilder().addAllStrips(strips).build();
        Playcloud.DecodeReply reply = blockingStub.decode(request);
        return reply.getDecBlock().toByteArray();
    }
}
