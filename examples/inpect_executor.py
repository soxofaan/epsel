import pyspark
import logging


def process(x):
    return (x, repr(logging.root.handlers))


def main():
    sc = pyspark.SparkContext.getOrCreate()

    result = (
        sc.parallelize(range(5))
            .map(process)
            .collect()
    )

    print(result)


if __name__ == '__main__':
    main()
