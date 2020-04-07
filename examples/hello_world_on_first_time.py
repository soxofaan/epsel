"""

Example `epsel` usage

Run on spark, for example as follows:

    spark-submit --master local[1]  examples/hello_world_on_first_time.py

"""

import pyspark

from epsel import on_first_time


@on_first_time(lambda: print("hello world"))
def process(x):
    return x * x


def main():
    sc = pyspark.SparkContext.getOrCreate()
    result = sc.parallelize(range(5)).map(process).collect()
    print(result)


if __name__ == '__main__':
    main()
