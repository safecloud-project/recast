package ch.unine.iiun.safecloud;

import java.io.IOException;
import java.util.Scanner;

public class Main {
    public static final int A_DAY_IN_MILLISECONDS = 1000 * 60 * 60 * 24;

    public static void main(String[] args) throws IOException, InterruptedException {
        Server server = new Server();
        server.start();
        while (true) {
            Thread.sleep(A_DAY_IN_MILLISECONDS);
        }
    }
}
