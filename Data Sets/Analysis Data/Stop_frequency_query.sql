SELECT t.trip_id, t.route_id, st.stop_id, st.arrival_time, r.route_long_name, s.stop_name, t.direction_id, s.stop_lat, s.stop_lon
FROM UCaglary.routes as r
JOIN UCaglary.trips as t on t.route_id = r.route_id
JOIN UCaglary.stop_times as st on st.trip_id = t.trip_id
JOIN UCaglary.stops as s on s.stop_id = st.stop_id
Where r.route_long_name Like "Blue%"
OR r.route_long_name Like "Red%"
OR r.route_long_name like "MAX%"
