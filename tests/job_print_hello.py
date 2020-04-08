import pyspark

import epsel


def hello():
    print("Hello world!")


@epsel.on_first_time(hello)
def process(x):
    return x * x


def main():
    sc = pyspark.SparkContext.getOrCreate()
    result = sc.parallelize(range(100)).map(process).collect()
    print(result)


if __name__ == '__main__':
    main()
