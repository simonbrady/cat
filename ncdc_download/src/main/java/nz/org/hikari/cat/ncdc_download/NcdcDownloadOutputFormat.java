package nz.org.hikari.cat.ncdc_download;

import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.lib.MultipleTextOutputFormat;

// Derived from https://stackoverflow.com/questions/18541503
public class NcdcDownloadOutputFormat extends MultipleTextOutputFormat<Text, Text> {

	// Use the key as part of the path for the final output file.
	@Override
	protected String generateFileNameForKeyValue(Text key, Text value, String leaf) {
		return new Path(key.toString(), leaf).toString();
	}

	// Discard key since it's only used to select the output file
	@Override
	protected Text generateActualKey(Text key, Text value) {
		return null;
	}
}
