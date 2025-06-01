import svg

class Skin(object):

    def __init__(self):
        self.title = svg.Style(font=svg.SansSerif('12px'))
        self.outer_border = svg.Style(stroke="grey", fill="white", stroke_width=2)
        self.inner_border = svg.Style(stroke="grey", fill="#E0E0E0", stroke_width=2)
        self.shape = svg.Style(stroke="black", fill=None, stroke_width=1)
        self.divisions = svg.Style(stroke="grey", fill=None, stroke_width=1, stroke_opacity="0.4")
        self.y_scale = 0.97
        self.y_divisions = 8

class ChartData(object):

    def __init__(self, series_order = None, data = None):
        self.data = data

        self.series_order = series_order
        if self.series_order is None:
            self.series_order = []

        for series_name in data:
            if series_name not in self.series_order:
                self.series_order.append(series_name)

class Chart(svg.SVGObject):

    def __init__(self, id, width, height, title, data):
        self.base_colors = [
            (100, 30, 22),
            (120, 40, 31),
            (81, 46, 95),
            (74, 35, 90),
            (21, 67, 96 ),
            (27, 79, 114),
            (14, 98, 81),
            (11, 83, 69 ),
            (20, 90, 50),
            (125, 102, 8),
            (126, 81, 9 ),
            (126, 81, 9),
            (120, 66, 18),
            (110, 44, 0),
        ]
        self.colors = [
           [
                "#{:02X}{:02X}{:02X}".format(
                    c[0] * (1 - x / 10) + (255 * x / 10),
                    c[1] * (1 - x / 10) + (255 * x / 10),
                    c[2] * (1 - x / 10) + (255 * x / 10)
                )
                for x in range(0, 10, 2)
           ] for c in self.base_colors
        ]
        self.data = data
        self.skin = Skin()
        super(Chart, self).__init__(
            "g",
            id,
            None,
            False,
            [
                svg.Rectangle("{0}-outline".format(id), 0, 0, width, height, self.skin.outer_border),
                svg.Text("{0}-title".format(id), 0, 12, title, self.skin.title),
            ]
        )
        self.children += self.create_chart()

    def create_chart(self):
        return []


class BarChart(Chart):

    def __init__(self, id, width, height, title, data):
        super(BarChart, self).__init__(id, width, height, title, data)
        self.data = data

    def create_chart(self):
        if self.data is None:
            return []

        min_x = None
        max_x = None
        min_y = None
        max_y = None

        for series_name in self.data.data:
            series_data = self.data.data[series_name]
            for data_point in series_data:
                if min_x is None or data_point < min_x:
                    min_x = data_point

                data_value = series_data[data_point]
                if min_y is None or data_value < min_y:
                    min_y = data_value

                if max_x is None or data_point > max_x:
                    max_x = data_point

                if max_y is None or data_value > max_y:
                    max_y = data_value

        if min_x is None or max_x is None:
            return []
        if min_y is None or max_y is None:
            return []

        y_division_height = float(max_y - min_y) / self.skin.y_divisions
        y_divisions = [ y_division_height * x + min_y for x in range(self.skin.y_divisions)]
        if min_x < 0 < max_x:
            y_divisions.append(0.0)

        bars = [
            svg.Rectangle(
                "{0}-bars-outline".format(self.get_id()),
                0,
                0,
                "100",
                "100",
                self.skin.inner_border
            )
        ]
        for series_idx in range(len(self.data.series_order)):
            color = self.colors[series_idx][0]
            series_name = self.data.series_order[series_idx]
            series_data = self.data.data[series_name]
            if isinstance(series_data, list):
                data_points = [ x for x in range(len(series_data))]
            elif isinstance(series_data, dict):
                data_points = series_data.keys()
                data_points.sort()
            else:
                raise Exception("ChartData.data must be Dict[List[Number]] or Dict[Dict[Any, Number]]")
            data_point_count = len(data_points)
            bar_width = 100.0 / data_point_count
            for data_point_idx in range(len(data_points)):
                data_point = data_points[data_point_idx]
                data_value = series_data[data_point]

                # x, y, width, height are all going to be relative to 100%
                x = data_point_idx * bar_width
                bar_height = self.skin.y_scale * 100 * data_value / max_y
                y = 100 - bar_height

                bar_style = self.skin.shape.copy()
                bar_style.set_fill(color)

                bars.append(svg.Rectangle(
                    "{0}-{1}-{2}".format(self.get_id(), series_name, data_point_idx),
                    "{:0.4f}".format(x),
                    "{:0.4f}".format(y),
                    "{:0.4f}".format(bar_width),
                    "{:0.4f}".format(bar_height),
                    bar_style
                ))

        for y_division in y_divisions:
            division_height = self.skin.y_scale * 100 * y_division / max_y
            y = 100 - division_height
            bars.append(svg.Line(
                "{0}-{1}-{2}".format(self.get_id(), "y", y_division),
                "0",
                "{:0.4f}".format(y),
                "100",
                "{:0.4f}".format(y),
                self.skin.divisions
            ))

        return [
            svg.SubSVG(
                "{0}-bars".format(self.get_id()),
                self.skin.inner_border,
                "5%",
                "10%",
                "90%",
                "80%",
                view_box="0 0 100 100",
                children=bars)
        ]