package ch.unine.iiun.safecloud;

import com.google.protobuf.ByteString;
import io.grpc.stub.StreamObserver;
import org.joda.time.DateTime;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.List;
import java.util.logging.Logger;

public class EncoderDecoderService implements EncoderDecoderGrpc.EncoderDecoder {

    private Logger logger;

    public EncoderDecoderService() {
        this.logger = Logger.getLogger(EncoderDecoderService.class.getSimpleName());
    }

    public void encode(Playcloud.EncodeRequest request, StreamObserver<Playcloud.EncodeReply> responseObserver) {
        DateTime start = new DateTime();
        ByteString payload = request.getPayload();
        Playcloud.EncodeReply reply = Playcloud.EncodeReply.newBuilder().setEncBlocks(payload).build();
        responseObserver.onNext(reply);
        responseObserver.onCompleted();
        DateTime end = new DateTime();
        long duration = end.minus(start.getMillis()).getMillis();
        logger.info("[ " + start.toString() + " ] encode " + duration + " ms");
    }

    public void decode(Playcloud.DecodeRequest request, StreamObserver<Playcloud.DecodeReply> responseObserver) {
        DateTime start = new DateTime();
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
        DateTime end = new DateTime();
        long duration = end.minus(start.getMillis()).getMillis();
        logger.info("[ " + start.toString() + " ] decode " + duration + " ms");
    }
}
