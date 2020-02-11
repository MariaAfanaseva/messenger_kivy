from matplotlib import pyplot
import numpy
from common.variables import get_path_diagram


class CreateDiagram:
    def __init__(self, database):
        self.database = database

    def diagram_all_messages(self):
        labels = []
        in_direction = []
        out_direction = []
        info_lst = self.database.get_col_messages()
        for i, data in enumerate(info_lst):
            if i % 2 == 0:
                labels.append(data[2])
                in_direction.append(data[0])
            else:
                out_direction.append(data[0])

        x = numpy.arange(len(labels))
        width = 0.35

        fig, ax = pyplot.subplots()
        rects1 = ax.bar(x - width / 2, in_direction, width, label='Incoming message')
        rects2 = ax.bar(x + width / 2, out_direction, width, label='Outgoing message')

        ax.set_ylabel('Count')
        ax.set_title('All messages')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()

        def autolabel(rects):
            """Attach a text label above each bar in *rects*, displaying its height."""
            for rect in rects:
                height = rect.get_height()
                ax.annotate('{}'.format(height),
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom')

        autolabel(rects1)
        autolabel(rects2)
        fig.tight_layout()
        fig.savefig(get_path_diagram('all_messages.jpg'))
