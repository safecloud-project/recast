package ch.unine.iiun.safecloud;

import java.io.IOException;
import java.util.Scanner;

public class Main {

    public static void main(String[] args) throws IOException, InterruptedException {
        Server server = new Server();
        server.start();
        while (true) {
            Thread.sleep(1000);
        }
    }
}
