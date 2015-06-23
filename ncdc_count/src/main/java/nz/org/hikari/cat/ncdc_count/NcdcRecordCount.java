package nz.org.hikari.cat.ncdc_count;

import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.reduce.LongSumReducer;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;

// Driver for NCDC record count MapReduce job
//
// Args: <input location> <output location>
//
//       e.g. s3://BUCKETNAME/ncdc/data/ /out
//
//       (note that /out will be created in HDFS, not the local filesystem,
//       and that it must not exist prior to running the job).
//
// Input: NCDC data files, optionally compressed in a MapReduce-compatible
//        format such as gzip or bzip2.
//
// Output: Tab-separated text file(s) containing the NCDC station ID (USAF and
//         WBAN identifiers concatenated, e.g. 029070-99999) and number of
//         input records for that station. There will be one output file per
//         reducer task, and the record count for a station will never be zero
//         because only station IDs seen in the input are counted.

public class NcdcRecordCount extends Configured implements Tool {

	public int run(String[] args) throws Exception {
		Job job = Job.getInstance(getConf(), "NCDC Record Count");
		job.setJarByClass(NcdcRecordCount.class);
		
		FileInputFormat.addInputPath(job, new Path(args[0]));
		FileOutputFormat.setOutputPath(job, new Path(args[1]));
		
		job.setMapperClass(NcdcRecordCountMapper.class);
		job.setCombinerClass(LongSumReducer.class);
		job.setReducerClass(LongSumReducer.class);

		job.setOutputKeyClass(Text.class);
		job.setOutputValueClass(LongWritable.class);
		
		return job.waitForCompletion(true) ? 0 : 1;
	}

	public static void main(String[] args) throws Exception {
		System.exit(ToolRunner.run(new NcdcRecordCount(), args));
	}

}
