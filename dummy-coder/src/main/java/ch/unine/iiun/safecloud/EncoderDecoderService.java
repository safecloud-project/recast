package ch.unine.iiun.safecloud;

import com.google.protobuf.ByteString;
import io.grpc.stub.StreamObserver;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.List;

public class EncoderDecoderService implements EncoderDecoderGrpc.EncoderDecoder {
    public void encode(Playcloud.EncodeRequest request, StreamObserver<Playcloud.EncodeReply> responseObserver) {
        ByteString payload = request.getPayload();
        Playcloud.EncodeReply reply = Playcloud.EncodeReply.newBuilder().setEncBlocks(payload).build();
        responseObserver.onNext(reply);
        responseObserver.onCompleted();
    }

    public void decode(Playcloud.DecodeRequest request, StreamObserver<Playcloud.DecodeReply> responseObserver) {
        List<ByteString> blockList = request.getEncBlocksList();
        ByteArrayOutputStream stream = new ByteArrayOutputStream();
        for (ByteString block : blockList) {
            try {
                block.writeTo(stream);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        ByteString payload = ByteString.copyFrom(stream.toByteArray());
        Playcloud.DecodeReply reply = Playcloud.DecodeReply.newBuilder().setDecBlock(payload).build();
        responseObserver.onNext(reply);
        responseObserver.onCompleted();
    }
}
