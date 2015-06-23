package nz.org.hikari.cat.ncdc_count;

import java.io.IOException;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

// Mapper for NCDC record count MapReduce job, called from NcdcRecordCount
// driver class

public class NcdcRecordCountMapper
		extends Mapper<LongWritable, Text, Text, LongWritable> {
	
	@Override
	public void map(LongWritable key, Text value, Context context)
			throws IOException, InterruptedException {
		String line = value.toString();
		String id = line.substring(4, 10) + "-" + line.substring(10, 15);
		context.write(new Text(id), new LongWritable(1L));
	}

}
