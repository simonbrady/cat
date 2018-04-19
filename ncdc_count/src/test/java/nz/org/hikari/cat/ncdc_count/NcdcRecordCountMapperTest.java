package nz.org.hikari.cat.ncdc_count;

// Unit tests for NcdcRecordCountMapper, based on the example in Tom White,
// "Hadoop: The Definitive Guide" (4th ed: O'Reilly, 2015), p153, but updated
// for Mockito since MRUnit has been retired. Mockito approach taken from
// https://stackoverflow.com/questions/47701421

import static org.mockito.Mockito.*;

import java.io.IOException;

import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.InOrder;
import org.mockito.Mock;
import org.mockito.junit.MockitoJUnitRunner;

@RunWith(MockitoJUnitRunner.class)
public class NcdcRecordCountMapperTest {

	private NcdcRecordCountMapper mapper;

	@Mock
	private NcdcRecordCountMapper.Context context;

	@Before
	public void setUp() throws Exception {
		mapper = new NcdcRecordCountMapper();
	}

	@Test
	public void testMap() throws IOException, InterruptedException {
		// Dummy offset
		LongWritable dummy = new LongWritable(0L);
		// Control data section of first record in 1901/029070-99999-1901.gz
		Text key1 = new Text("029070-99999");
		Text value1 = new Text("0029029070999991901010106004+64333+023450FM-12+000599999V020");
		// Control data section of first record in 1901/029500-99999-1901.gz
		Text key2 = new Text("029500-99999");
		Text value2 = new Text("0029029500999991901010106004+61483+021350FM-12+000699999V020");
		// Control data section of second record in 1901/029070-99999-1901.gz
		Text key3 = new Text("029070-99999");
		Text value3 = new Text("0029029070999991901010113004+64333+023450FM-12+000599999V020");
		// Expected count
		LongWritable one = new LongWritable(1L);
		// Wrapper to verify that results are written in the correct order
		InOrder ordered = inOrder(context);

		mapper.map(dummy, value1, context);
		mapper.map(dummy, value2, context);
		mapper.map(dummy, value3, context);
		ordered.verify(context).write(key1, one);
		ordered.verify(context).write(key2, one);
		ordered.verify(context).write(key3, one);
	}

	@After
	public void tearDown() throws Exception {
		verifyNoMoreInteractions(context);
	}

}
