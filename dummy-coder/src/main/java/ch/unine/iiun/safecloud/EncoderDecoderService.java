package ch.unine.iiun.safecloud;

import com.google.protobuf.ByteString;
import io.grpc.stub.StreamObserver;

public class EncoderDecoderService implements EncoderDecoderGrpc.EncoderDecoder {


    public void encode(Playcloud.EncodeRequest request, StreamObserver<Playcloud.EncodeReply> responseObserver) {
        ByteString payload = request.getPayload();
        Playcloud.EncodeReply reply = Playcloud.EncodeReply.newBuilder().setEncBlocks(payload).build();
        responseObserver.onNext(reply);
        responseObserver.onCompleted();
    }

    public void decode(Playcloud.DecodeRequest request, StreamObserver<Playcloud.DecodeReply> responseObserver) {
        ByteString payload = request.getEncBlocks();
        Playcloud.DecodeReply reply = Playcloud.DecodeReply.newBuilder().setDecBlock(payload).build();
        responseObserver.onNext(reply);
        responseObserver.onCompleted();
    }
}
