package ch.unine.iiun.safecloud.microbench;

import ch.unine.iiun.safecloud.EncoderDecoderGrpc;
import ch.unine.iiun.safecloud.Playcloud;
import com.google.protobuf.ByteString;
import io.grpc.internal.ManagedChannelImpl;
import io.grpc.netty.NegotiationType;
import io.grpc.netty.NettyChannelBuilder;

import java.util.GregorianCalendar;

public class Client {

    private ManagedChannelImpl channel;
    private EncoderDecoderGrpc.EncoderDecoderBlockingStub stub;
    private String host;
    private int port;

    public Client(final String host, final int port) {
        this.host = host;
        this.port = port;
        if (this.channel == null) {
            this.channel = NettyChannelBuilder.forAddress(this.host, this.port)
                    .negotiationType(NegotiationType.PLAINTEXT)
                    .build();
        }
        if (this.stub == null) {
            this.stub = EncoderDecoderGrpc.newBlockingStub(channel);
        }
    }

    public long encode(final byte[] data) throws Throwable {
        ;
        long start = (new GregorianCalendar()).getTimeInMillis();
        try {
            Playcloud.EncodeRequest request = Playcloud.EncodeRequest.newBuilder().setPayload(ByteString.copyFrom(data)).build();
            this.stub.encode(request);
        } catch (Throwable t) {
            t.printStackTrace();
            throw t;
        }
        long end = (new GregorianCalendar()).getTimeInMillis();
        return end - start;
    }
}
