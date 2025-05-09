
def get_chart_meta_info():
    """
    Extract comprehensive chart metadata from the frontend graph configuration.
    Returns a list of chart metadata objects with detailed formatting requirements.
    """
    # This would typically be loaded from a configuration file or database
    chart_meta_info = [
        {
            "id": 1,
            "name": "Line Chart",
            "category": "Line Chart",
            "dataFormat": {
                "structure": "rows",
                "required_columns": ["category/name", "measure"],
                "recommended_data": {
                    "x_axis": "date or sequential category",
                    "y_axis": "numeric values"
                },
                "example_mapping": {
                    "name": "x-axis category",
                    "uv/pv/amt": "y-axis values"
                }
            },
            "sql_template": "SELECT time_column as name, measure_column as value FROM table ORDER BY time_column"
        },
        {
            "id": 2,
            "name": "Stacked Area Chart",
            "category": "Line Chart",
            "dataFormat": {
                "structure": "rows",
                "required_columns": ["category/name", "multiple measures"],
                "recommended_data": {
                    "x_axis": "date or sequential category",
                    "y_axis": "multiple numeric values that can be stacked"
                },
                "example_mapping": {
                    "name": "x-axis category",
                    "dataKeys": ["uv", "pv", "amt"]
                }
            },
            "sql_template": "SELECT category as name, measure1, measure2, measure3 FROM table GROUP BY category"
        },
        {
            "id": 3,
            "name": "Customize Line Chart",
            "category": "Line Chart",
            "dataFormat": {
                "structure": "rows with config",
                "required_columns": ["category/name", "multiple measures"],
                "config_options": ["stroke color", "dataKey mapping"],
                "example_mapping": {
                    "data": [{"name": "category", "measure1": 123, "measure2": 456}],
                    "config": [{"dataKey": "measure1", "stroke": "#color"}]
                }
            },
            "sql_template": "SELECT category as name, measure1, measure2 FROM table GROUP BY category"
        },
        {
            "id": 4,
            "name": "Simple Bar Chart",
            "category": "Bar Chart",
            "dataFormat": {
                "structure": "rows with bar config",
                "required_columns": ["category/name", "measure values"],
                "example_mapping": {
                    "data": [{"name": "category", "measure1": 123, "measure2": 456}],
                    "bars": [{"dataKey": "measure1"}, {"dataKey": "measure2"}]
                }
            },
            "sql_template": "SELECT category as name, SUM(value1) as measure1, SUM(value2) as measure2 FROM table GROUP BY category"
        },
        {
            "id": 5,
            "name": "Customize Shape Bar Chart",
            "category": "Bar Chart",
            "dataFormat": {
                "structure": "rows with single dataKey",
                "required_columns": ["category/name", "primary measure"],
                "example_mapping": {
                    "data": [{"name": "category", "uv": 123, "pv": 456}],
                    "dataKey": "uv"
                }
            },
            "sql_template": "SELECT category as name, SUM(value) as uv FROM table GROUP BY category"
        },
        {
            "id": 6,
            "name": "Line And Bar Chart",
            "category": "Bar Chart",
            "dataFormat": {
                "structure": "rows with multiple config",
                "required_columns": ["category/name", "4 different measures"],
                "component_mapping": {
                    "areaConfig": {"dataKey": "amt"},
                    "barConfig": {"dataKey": "pv"},
                    "lineConfig": {"dataKey": "uv"},
                    "scatterConfig": {"dataKey": "cnt"}
                }
            },
            "sql_template": "SELECT category as name, sum(measure1) as uv, sum(measure2) as pv, sum(measure3) as amt, count(*) as cnt FROM table GROUP BY category"
        },
        {
            "id": 7,
            "name": "Pie Chart",
            "category": "Pie Chart",
            "dataFormat": {
                "structure": "name-value pairs",
                "required_columns": ["name", "value"],
                "example_mapping": {
                    "data": [{"name": "Category 1", "value": 500}],
                    "dataKey": "value"
                }
            },
            "sql_template": "SELECT category as name, SUM(value) as value FROM table GROUP BY category"
        },
        {
            "id": 8,
            "name": "Geo Chart",
            "category": "Others",
            "dataFormat": {
                "structure": "rows",
                "required_columns": ["region/location name", "measure values"],
                "geo_requirements": "Region names must match map data"
            },
            "sql_template": "SELECT region_name as name, SUM(value) as uv FROM table GROUP BY region_name"
        },
        {
            "id": 9,
            "name": "Radar Chart",
            "category": "Others",
            "dataFormat": {
                "structure": "rows with radar configs",
                "required_columns": ["subject/category", "multiple measures"],
                "example_mapping": {
                    "data": [{"subject": "Category", "A": 120, "B": 110}],
                    "radarConfigs": [
                        {"name": "Series A", "dataKey": "A"},
                        {"name": "Series B", "dataKey": "B"}
                    ]
                }
            },
            "sql_template": "SELECT dimension as subject, AVG(metric1) as A, AVG(metric2) as B FROM table GROUP BY dimension"
        },
        {
            "id": 10,
            "name": "Radial Chart",
            "category": "Others",
            "dataFormat": {
                "structure": "rows with dataKey",
                "required_columns": ["name", "value column (usually percentage)"],
                "example_mapping": {
                    "data": [{"name": "18-24", "uv": 31.47}],
                    "dataKey": "uv"
                }
            },
            "sql_template": "SELECT category as name, percentage as uv FROM table ORDER BY uv DESC"
        },
        {
            "id": 11,
            "name": "card",
            "category": "Others",
            "dataFormat": {
                "structure": "summary values",
                "required_columns": ["name", "metric values"],
                "typical_usage": "Showing KPIs or summary metrics"
            },
            "sql_template": "SELECT SUM(value) as value FROM table"
        }
    ]

    return chart_meta_info