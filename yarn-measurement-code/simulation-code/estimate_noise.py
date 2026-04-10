import csv
import numpy as np

with open('measured-seven-set.csv') as csvfile:
	reader = csv.reader(csvfile)
	heading = next(reader)
	stitches = next(reader)
	assert(stitches[0] == 'Swatch')
	assert(stitches[1] == 'Trial #')

	#get the columns for just the 30/25 trials:
	wanted = []
	for i in range(len(stitches)):
		if stitches[i] == '110: 30/25':
			wanted.append(i)

	print("Using columns: ", wanted)

	#skip the tag # row:
	tagNum = next(reader)
	assert(tagNum[0] == 'Tag #')

	#the ratio between reported weight and mean weight:
	# (approximately: relative error of the scale for each weighing)
	weight_proportion = []

	#the ratio (per sample) between sample weight and mean sample weight:
	# (approximately: relative error owing to machine + yarn variation)
	sample_proportion = []

	#for each sample...
	for sampleNum in range(7):
		#grab the three weighing trials:
		weighings = []
		weighings.append(next(reader))
		weighings.append(next(reader))
		weighings.append(next(reader))
		assert(weighings[0][1] == '1')
		assert(weighings[1][1] == '2')
		assert(weighings[2][1] == '3')

		print(f"Sample: {weighings[0][0]}")

		means = []

		for col in wanted:
			#skip failed samples:
			if weighings[0][col] == '-': continue

			weights = np.array([float(weighings[i][col]) for i in range(len(weighings))])
			mean = np.mean(weights)
			weight_proportion += list(weights / mean)
			means.append(mean)

		#compute proportional variation of sample weight vs mean of all samples of this type:
		means = np.array(means)
		mean_means = np.mean(means)
		sample_proportion += list(means / mean_means)
		print(f"  relative to avg: {means / mean_means}")
		

		#skip the 'avg' row:
		avg = next(reader)
		assert(avg[1] == 'avg')
	
	print(weight_proportion)
	print(sample_proportion)

	print(f"measured weight ratio (count: {len(weight_proportion)}) had mean {np.mean(weight_proportion)} and stddev {np.std(weight_proportion)}.")

	print(f"sample weight ratio (count: {len(sample_proportion)}) had mean {np.mean(sample_proportion)} and stddev {np.std(sample_proportion)}.")
	
	#make sure we get the row after the data:
	after = next(reader)
	assert(after[0] == 'Cone')
