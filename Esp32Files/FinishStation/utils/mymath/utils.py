#------------aux functions--------------#
def mode(dataset):
    frequency = {}
    for value in dataset:
        frequency[value] = frequency.get(value, 0) + 1
    most_frequent = max(frequency.values())
    modes = [key for key, value in frequency.items()
                      if value == most_frequent]
    return modes

def mean(dataset):
    return sum(dataset) / len(dataset)

def median(dataset):
    data = sorted(dataset)
    index = len(data) // 2
    # If the dataset is odd  
    if len(dataset) % 2 != 0:
        return data[index]
    # If the dataset is even
    return (data[index - 1] + data[index]) / 2