package nz.org.hikari.cat.ncdc_download;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNull;

import org.apache.hadoop.io.Text;
import org.junit.Test;

public class NcdcDownloadOutputFormatTest {

	@Test
	public void checkPath() {
		NcdcDownloadOutputFormat outputFormat = new NcdcDownloadOutputFormat();
		String path = outputFormat.generateFileNameForKeyValue(new Text("1901"),
			new Text("value"), "filename.bz2");
		assertEquals(path, "1901/filename.bz2");
	}

	@Test
	public void checkKey()
	{
		NcdcDownloadOutputFormat outputFormat = new NcdcDownloadOutputFormat();
		Text key = outputFormat.generateActualKey(new Text("1901"), new Text("value"));
		assertNull(key);
	}

}
