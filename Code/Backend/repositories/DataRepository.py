from .Database import Database


class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens

    @staticmethod
    def read_time_limits():
        sql = "Select * FROM Project.TimeLimit Where idTimeLimit=1"
        return Database.get_one_row(sql)
    
    @staticmethod
    def update_TimeLimits(startTime, stopTime):
        sql = 'Update Project.TimeLimit Set startTime = %s, stopTime = %s Where idTimeLimit = 1'
        params = [startTime, stopTime]
        return Database.execute_sql(sql,params)

    @staticmethod
    def read_sensorname_by_id(id):
        sql = "Select * FROM Project.Devices WHERE DeviceID = %s"
        params = [id]
        return Database.get_one_row(sql, params)
    
    @staticmethod
    def read_deviceID_by_name(name):
        sql = "Select DeviceID FROM Project.Devices WHERE DeviceName = %s"
        params = [name]
        return Database.get_one_row(sql, params)    
    
#region Pictures
    @staticmethod
    def get_latest_picture_date():
        sql = "Select MAX(DateTime) as DateTime FROM Project.Pictures"
        return Database.get_one_row(sql)
    
    @staticmethod
    def get_picture_locations():
        sql = "Select * FROM Project.Pictures WHERE DateTime > now()-INTERVAL 30 day"
        return Database.get_rows(sql)

    @staticmethod
    def insert_new_picture_location(location, datetime, id):
        sql = "INSERT INTO Project.Pictures (imageLocation, DateTime, DeviceID) Values(%s, %s, %s)"
        params = [location, datetime, id]
        return Database.execute_sql(sql,params)
#endregion

#region Data
    @staticmethod
    def insert_sensordata(id, datetime, value):
        sql = 'INSERT INTO Project.DeviceData (DateTime, Value, DeviceID) Values(%s, %s, %s)'
        params = [datetime, value, id]
        return Database.execute_sql(sql, params)

    @staticmethod
    def read_sensor_data_by_id(id, days):
    #     sql = "Select Value FROM Project.DeviceData WHERE DeviceID = %s and DateTime > now()-INTERVAL %s day"
        sql = "SELECT date_format(DateTime, '%Y-%m-%d %H:%i') as DateTime, avg(Value) as Value, DeviceID FROM Project.DeviceData WHERE DeviceID = %s GROUP BY DATE(DateTime), hour(DateTime) having DateTime > Now() - INTERVAL %s DAY ORDER BY DateTime"
        params = [id, days]
        return Database.get_rows(sql, params)

    @staticmethod
    def clear_old_data():
        sql = "DELETE FROM Project.DeviceData WHERE DateTime < now()-INTERVAL 7 day"
        Database.execute_sql(sql)
        sql = "DELETE FROM Project.Pictures WHERE DateTime < now()-INTERVAL 7 day"
        return Database.execute_sql(sql)
#endregion

#region Settings
    @staticmethod
    def read_sensor_settings():
        sql = "Select * FROM Project.DeviceSettings"
        return Database.get_rows(sql)

    @staticmethod
    def read_sensor_settings_by_id(id):
        sql = "Select * FROM Project.DeviceSettings Where DeviceID = %s"
        params = [id]
        return Database.get_one_row(sql, params)

    @staticmethod
    def read_data_setting(name):
        sql = "Select SpeedInSeconds FROM Project.DataSettings WHERE Name = %s"
        params = [name]
        return Database.get_one_row(sql, params)
    
    @staticmethod
    def read_data_settings_all():
        sql = "Select * FROM Project.DataSettings"
        return Database.get_rows(sql)

    @staticmethod
    def update_sensorsettings(id, UpperLimit, LowerLimit, Active):
        sql = 'Update Project.DeviceSettings Set UpperLimit = %s, LowerLimit = %s, Active = %s Where DeviceID = %s'
        params = [UpperLimit, LowerLimit, Active, id]
        return Database.execute_sql(sql, params)

    @staticmethod
    def update_datasettings(Speed, Name):
        sql = 'Update Project.DataSettings Set SpeedInSeconds = %s Where Name = %s'
        params = [Speed, Name]
        print(params)
        return Database.execute_sql(sql, params)
#endregion
    

