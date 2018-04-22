package nz.org.hikari.cat.ncdc_extract;

// Unit tests for NcdcExtractReducer

import static org.mockito.Mockito.*;

import java.lang.reflect.Field;
import java.util.ArrayList;

import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Counter;
import org.apache.hadoop.mapreduce.lib.output.MultipleOutputs;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mock;
import org.mockito.junit.MockitoJUnitRunner;

@RunWith(MockitoJUnitRunner.class)
public class NcdcExtractReducerTest {

	private NcdcExtractReducer reducer;

	@Mock
	private NcdcExtractReducer.Context context;

	@Mock
	private MultipleOutputs<NullWritable, Text> multipleOutputs;

	@Mock
	private Counter stationCounter;

	@Before
	public void setUp() throws Exception {
		reducer = new NcdcExtractReducer();
	}

	@Test
	public void testReduce() throws Exception {
		// Station to extract
		String station = "029070-99999";
		Text key = new Text(station);
		// Control data section of first record in 1901/029070-99999-1901.gz
		Text value1 = new Text("0029029070999991901010106004+64333+023450FM-12+000599999V020");
		// Control data section of second record in 1901/029070-99999-1901.gz
		Text value2 = new Text("0029029070999991901010113004+64333+023450FM-12+000599999V020");
		// List of values to reduce
		ArrayList<Text> values = new ArrayList<>();
		values.add(value1);
		values.add(value2);

		when(context.getCounter(Constants.COUNTER_GROUP, station))
			.thenReturn(stationCounter);

		// Simulate call to reducer.setup()
		Field mapperMultipleOutputs = NcdcExtractReducer.class.getDeclaredField("multipleOutputs");
		mapperMultipleOutputs.setAccessible(true);
		mapperMultipleOutputs.set(reducer, multipleOutputs);

		reducer.reduce(key, values, context);
		reducer.cleanup(context);

		verify(context, times(2)).getCounter(eq(Constants.COUNTER_GROUP), anyString());
		verify(stationCounter, times(2)).increment(1);
		verify(multipleOutputs).write(NullWritable.get(), value1, station);
		verify(multipleOutputs).write(NullWritable.get(), value2, station);
		verify(multipleOutputs).close();
	}

	@After
	public void tearDown() throws Exception {
		verifyNoMoreInteractions(context);
		verifyNoMoreInteractions(stationCounter);
		verifyNoMoreInteractions(multipleOutputs);
	}

}
