package ch.unine.iiun.safecloud;

import com.google.protobuf.ByteString;
import io.grpc.internal.ManagedChannelImpl;
import io.grpc.netty.NegotiationType;
import io.grpc.netty.NettyChannelBuilder;

public class ErasureClient {

    public static final String DEFAULT_HOST = "127.0.0.1";
    public static final int DEFAULT_PORT = 1234;

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

    public byte[] encode(byte[] data) {
        setUp();
        ByteString payload = ByteString.copyFrom(data);
        Playcloud.EncodeRequest request = Playcloud.EncodeRequest.newBuilder().setPayload(payload).build();
        Playcloud.EncodeReply reply = blockingStub.encode(request);
        return reply.getEncBlocks().toByteArray();
    }

    public byte[] decode(byte[] data) {
        setUp();
        ByteString payload = ByteString.copyFrom(data);
        Playcloud.DecodeRequest request = Playcloud.DecodeRequest.newBuilder().addEncBlocks(payload).build();
        Playcloud.DecodeReply reply = blockingStub.decode(request);
        return reply.getDecBlock().toByteArray();
    }
}
