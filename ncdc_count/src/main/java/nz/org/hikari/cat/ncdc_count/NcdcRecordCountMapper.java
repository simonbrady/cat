package nz.org.hikari.cat.ncdc_count;

// Mapper for NCDC record count MapReduce job, called from NcdcRecordCount
// driver class

import java.io.IOException;

import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

public class NcdcRecordCountMapper
		extends Mapper<LongWritable, Text, Text, LongWritable> {
	
	static final LongWritable one = new LongWritable(1);

	@Override
	public void map(LongWritable key, Text value, Context context)
			throws IOException, InterruptedException {
		String line = value.toString();
		String id = line.substring(4, 10) + "-" + line.substring(10, 15);
		context.write(new Text(id), one);
	}

}
