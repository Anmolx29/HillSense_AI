import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_database/firebase_database.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await Firebase.initializeApp();

  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,

      title: 'HillSense AI',

      theme: ThemeData.dark(),

      home: DashboardPage(),
    );
  }
}

class DashboardPage extends StatefulWidget {
  @override
  _DashboardPageState createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  final DatabaseReference sensorRef = FirebaseDatabase.instance.ref('sensor');

  final DatabaseReference predictionRef = FirebaseDatabase.instance.ref(
    'prediction',
  );

  double temperature = 0;
  double humidity = 0;
  double moisture = 0;

  String soilQuality = 'Loading...';
  String irrigation = 'Loading...';
  String crop = 'Loading...';
  String fertilizer = 'Loading...';

  @override
  void initState() {
    super.initState();

    fetchData();
  }

  void fetchData() {
    sensorRef.onValue.listen((event) {
      final data = event.snapshot.value as Map<dynamic, dynamic>?;

      if (data != null) {
        setState(() {
          temperature = (data['temperature'] ?? 0).toDouble();

          humidity = (data['humidity'] ?? 0).toDouble();

          moisture = (data['moisture'] ?? 0).toDouble();
        });
      }
    });

    predictionRef.onValue.listen((event) {
      final data = event.snapshot.value as Map<dynamic, dynamic>?;

      if (data != null) {
        setState(() {
          soilQuality = data['soil_quality'] ?? 'Unknown';

          irrigation = data['irrigation'] ?? 'Unknown';

          crop = data['crop'] ?? 'Unknown';

          fertilizer = data['fertilizer'] ?? 'Unknown';
        });
      }
    });
  }

  Widget sensorCard(String title, String value, IconData icon, Color color) {
    return Container(
      margin: EdgeInsets.all(8),

      padding: EdgeInsets.all(20),

      decoration: BoxDecoration(
        color: Colors.grey[900],

        borderRadius: BorderRadius.circular(20),
      ),

      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,

        children: [
          Icon(icon, size: 40, color: color),

          SizedBox(height: 10),

          Text(title, style: TextStyle(fontSize: 18)),

          SizedBox(height: 10),

          Text(
            value,
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }

  Widget recommendationCard(String title, String value, Color color) {
    return Container(
      width: double.infinity,

      margin: EdgeInsets.symmetric(vertical: 8),

      padding: EdgeInsets.all(20),

      decoration: BoxDecoration(
        color: color.withOpacity(0.2),

        borderRadius: BorderRadius.circular(20),

        border: Border.all(color: color),
      ),

      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,

        children: [
          Text(
            title,
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),

          SizedBox(height: 10),

          Text(value, style: TextStyle(fontSize: 16)),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('🌱 HillSense AI'), centerTitle: true),

      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),

        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,

          children: [
            Text(
              '📡 Live Sensor Data',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),

            SizedBox(height: 10),

            GridView.count(
              crossAxisCount: 2,

              shrinkWrap: true,

              physics: NeverScrollableScrollPhysics(),

              children: [
                sensorCard(
                  'Temperature',
                  '${temperature.toStringAsFixed(1)} °C',
                  Icons.thermostat,
                  Colors.red,
                ),

                sensorCard(
                  'Humidity',
                  '${humidity.toStringAsFixed(1)} %',
                  Icons.water_drop,
                  Colors.blue,
                ),

                sensorCard(
                  'Moisture',
                  '${moisture.toStringAsFixed(1)} %',
                  Icons.grass,
                  Colors.green,
                ),

                sensorCard(
                  'Soil Quality',
                  soilQuality,
                  Icons.analytics,
                  Colors.orange,
                ),
              ],
            ),

            SizedBox(height: 20),

            Text(
              '🤖 Smart Recommendations',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),

            SizedBox(height: 10),

            recommendationCard('💧 Irrigation', irrigation, Colors.blue),

            recommendationCard('🌾 Recommended Crop', crop, Colors.green),

            recommendationCard('🧪 Fertilizer', fertilizer, Colors.orange),
          ],
        ),
      ),
    );
  }
}
