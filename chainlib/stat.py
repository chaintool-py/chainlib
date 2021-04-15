import datetime

class ChainStat:

    def __init__(self):
        self.block_timestamp_last = None
        self.block_avg_aggregate = None
        self.block_avg_count = -1


    def block_apply(self, block):
        if self.block_timestamp_last == None:
            self.block_timestamp_last = block.timestamp
        
        aggregate = block.timestamp - self.block_timestamp_last

        if self.block_avg_aggregate == None:
            self.block_avg_aggregate = float(aggregate)
        else:
            self.block_avg_aggregate *= self.block_avg_count
            self.block_avg_aggregate += block.timestamp - self.block_timestamp_last
            self.block_avg_aggregate /= (self.block_avg_count + 1)

        self.block_avg_count += 1

        self.block_timestamp_last = block.timestamp

    def block_average(self):
        return self.block_avg_aggregate
