import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.net.ServerSocket;
import java.net.Socket;

public class FileServer {

	public final static int SOCKET_PORT = 1337;
	public final static String FILE_TO_SEND = "./maintenance_data.txt";

	public static void main(final String[] args) throws IOException {
		FileInputStream fis = null;
		BufferedInputStream bis = null;
		OutputStream os = null;
		ServerSocket servsock = null;
		Socket sock = null;
		try {
			servsock = new ServerSocket(SOCKET_PORT);
			// servsock.setSoTimeout(60*1000);
			System.out.println("Waiting...");
			while (true) {
				try {
					sock = servsock.accept();
					System.out.println("Accepted connection : " + sock);
					// send file
					final File myFile = new File(FILE_TO_SEND);
					final byte[] mybytearray = new byte[(int) myFile.length()];
					fis = new FileInputStream(myFile);
					bis = new BufferedInputStream(fis);
					bis.read(mybytearray, 0, mybytearray.length);
					os = sock.getOutputStream();
					System.out.println("Sending " + FILE_TO_SEND + "(" + mybytearray.length + " bytes)");
					os.write(mybytearray, 0, mybytearray.length);
					os.flush();
				} finally {
					if (bis != null) {
						bis.close();
					}
					if (os != null) {
						os.close();
					}
					if (sock != null) {
						sock.close();
					}
				}
			}
		} finally {
			if (servsock != null) {
				servsock.close();
			}
		}
	}
}
