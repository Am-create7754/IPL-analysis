import pandas as pd
import numpy as np
import os

def generate_mock_data():
    os.makedirs('data', exist_ok=True)
    
    players_raw = [
    
        ("Virat Kohli", "Bat", "Right", 175), ("Rohit Sharma", "Bat", "Right", 174), ("MS Dhoni", "Bat", "Right", 175),
        ("Jasprit Bumrah", "Fast", "Right", 175), ("Hardik Pandya", "All_Fast", "Right", 183), ("Ravindra Jadeja", "All_Spin", "Left", 173),
        ("Shubman Gill", "Bat", "Right", 185), ("KL Rahul", "Bat", "Right", 184), ("Rishabh Pant", "Bat", "Left", 170),
        ("Shreyas Iyer", "Bat", "Right", 178), ("Mohammed Shami", "Fast", "Right", 178), ("Mohammed Siraj", "Fast", "Right", 178),
        ("Kuldeep Yadav", "Spin", "Left", 168), ("Yuzvendra Chahal", "Spin", "Right", 168), ("Axar Patel", "All_Spin", "Left", 182),
        ("Suryakumar Yadav", "Bat", "Right", 180), ("Ishan Kishan", "Bat", "Left", 168), ("Sanju Samson", "Bat", "Right", 170),
        ("Bhuvneshwar Kumar", "Fast", "Right", 175), ("Shardul Thakur", "Fast", "Right", 175), ("Yashasvi Jaiswal", "Bat", "Left", 183),
        ("Rinku Singh", "Bat", "Left", 165), ("Tilak Varma", "Bat", "Left", 180), ("Ruturaj Gaikwad", "Bat", "Right", 175),
        ("Arshdeep Singh", "Fast", "Left", 190), ("Umran Malik", "Fast", "Right", 178), ("Ravi Bishnoi", "Spin", "Right", 170),
        ("Washington Sundar", "All_Spin", "Left", 185), ("Deepak Chahar", "Fast", "Right", 178), ("Ishant Sharma", "Fast", "Right", 193),
        ("Umesh Yadav", "Fast", "Right", 180), ("Varun Chakravarthy", "Spin", "Right", 175), ("Venkatesh Iyer", "All_Fast", "Left", 191),
        ("Prithvi Shaw", "Bat", "Right", 165), ("Dinesh Karthik", "Bat", "Right", 170), ("Shikhar Dhawan", "Bat", "Left", 180),
        ("Rahul Tripathi", "Bat", "Right", 175), ("Shivam Dube", "All_Fast", "Left", 193),
        
        # --- Overseas IPL Stars ---
        ("David Warner", "Bat", "Left", 170), ("Jos Buttler", "Bat", "Right", 180), ("Glenn Maxwell", "All_Spin", "Right", 182),
        ("Faf du Plessis", "Bat", "Right", 180), ("Rashid Khan", "Spin", "Right", 172), ("Trent Boult", "Fast", "Right", 180),
        ("Kagiso Rabada", "Fast", "Left", 191), ("Sam Curran", "All_Fast", "Left", 175), ("Liam Livingstone", "All_Spin", "Right", 183),
        ("Sunil Narine", "All_Spin", "Left", 180), ("Andre Russell", "All_Fast", "Right", 185), ("Moeen Ali", "All_Spin", "Left", 183),
        ("Marcus Stoinis", "All_Fast", "Right", 185), ("Nicholas Pooran", "Bat", "Left", 173), ("Quinton de Kock", "Bat", "Left", 173),
        ("Pat Cummins", "Fast", "Right", 192), ("Mitchell Starc", "Fast", "Left", 197), ("Jofra Archer", "Fast", "Right", 182),
        ("Devon Conway", "Bat", "Left", 180), ("Harry Brook", "Bat", "Right", 180), ("Cameron Green", "All_Fast", "Right", 198),
        ("Lockie Ferguson", "Fast", "Right", 185), ("Anrich Nortje", "Fast", "Right", 185), ("Jason Holder", "All_Fast", "Right", 201),
        ("Kieron Pollard", "All_Fast", "Right", 196), ("Chris Gayle", "All_Spin", "Left", 188), ("AB de Villiers", "Bat", "Right", 178),
        
        # --- Legends ---
        ("Sachin Tendulkar", "Bat", "Right", 165), ("Zaheer Khan", "Fast", "Right", 180), ("Yuvraj Singh", "Bat", "Left", 188),
        ("Suresh Raina", "Bat", "Left", 175), ("Harbhajan Singh", "Spin", "Right", 180), ("Lasith Malinga", "Fast", "Right", 173),
        ("Dale Steyn", "Fast", "Right", 179), ("Shane Watson", "All_Fast", "Right", 183), ("Gautam Gambhir", "Bat", "Left", 168)
    ]
    
    bio_list = []
    telemetry_list = []
    
    avatar_map = {
        'Bat': 'https://cdn-icons-png.flaticon.com/512/2855/2855642.png',
        'Fast': 'https://cdn-icons-png.flaticon.com/512/861/861506.png',
        'Spin': 'https://cdn-icons-png.flaticon.com/512/861/861506.png',
        'All_Fast': 'https://cdn-icons-png.flaticon.com/512/2855/2855642.png',
        'All_Spin': 'https://cdn-icons-png.flaticon.com/512/2855/2855642.png'
    }

    special_images = {
        'Jasprit Bumrah': 'https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/IPLHeadshot2023/1124.png',
        'Virat Kohli': 'https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/IPLHeadshot2023/164.png',
        'MS Dhoni': 'https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/IPLHeadshot2023/1.png',
        'Rohit Sharma': 'https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/IPLHeadshot2023/107.png'
    }
    
    for name, role, hand, height in players_raw:
        weight = height - 100 + np.random.randint(-5, 6)
        
        if role == 'Fast' or role == 'All_Fast':
            core_speed = round(np.random.uniform(130.0, 155.0), 1)
            release_height = round(height / 100 + np.random.uniform(0.1, 0.3), 2)
            telemetry_speed_range = (130, 150)
            dev_range = (-1, 1) # Less spin deviation, more seam
            bounce_range = (0.8, 1.5)
        elif role == 'Spin' or role == 'All_Spin':
            core_speed = round(np.random.uniform(80.0, 105.0), 1)
            release_height = round(height / 100 + np.random.uniform(0.0, 0.2), 2)
            telemetry_speed_range = (80, 100)
            dev_range = (-4, 4) # More spin deviation
            bounce_range = (0.4, 0.9)
        else:
            core_speed = round(np.random.uniform(110.0, 125.0), 1)
            release_height = round(height / 100 + np.random.uniform(0.0, 0.2), 2)
            telemetry_speed_range = (100, 120)
            dev_range = (-1, 1)
            bounce_range = (0.5, 1.0)
            
        injury_index = np.random.randint(70, 99)
        
        img_url = special_images.get(name, avatar_map[role])
        
        bio_list.append({
            'player_name': name,
            'image_url': img_url,
            'dominant_hand': hand,
            'height_cm': height,
            'weight_kg': weight,
            'bowling_release_point_height_m': release_height,
            'max_recorded_core_speed_kmh': core_speed,
            'shoulder_ankle_injury_threshold_index': injury_index
        })
        
        # Generate Telemetry for this player
        num_balls = np.random.randint(30, 60)
        venues = ['Wankhede Red Soil', 'Chepauk Black Soil', 'Eden Gardens Clay']
        pressures = ['Low', 'High']
        
        for _ in range(num_balls):
            venue = np.random.choice(venues)
            pressure = np.random.choice(pressures)
            
            # Base values
            speed = np.random.uniform(*telemetry_speed_range)
            deviation = np.random.uniform(*dev_range)
            bounce = np.random.uniform(*bounce_range)
            pitch_dist = np.random.uniform(1.5, 7)
            
            # Venue impact
            if venue == 'Wankhede Red Soil':
                bounce *= 1.2  # Extra bounce
                deviation *= 0.8 # Less swing/spin
            elif venue == 'Chepauk Black Soil':
                bounce *= 0.85 # Low bounce
                deviation *= 1.3 # High spin/swing
                
            # Pressure impact (Choke logic)
            if pressure == 'High':
                speed *= np.random.uniform(0.92, 0.98)  # Speed drop 2-8%
                pitch_dist *= np.random.uniform(1.1, 1.4)  # Worse accuracy (wider)
                
            telemetry_list.append({
                'player_name': name,
                'session_date': '2026-06-05',
                'venue_soil_type': venue,
                'pressure_scenario': pressure,
                'release_speed': speed,
                'release_angle': np.random.uniform(8, 16),
                'deviation_degrees': deviation,
                'pitch_distance_from_stumps_m': pitch_dist,
                'bounce_height_m': bounce
            })
            
    pd.DataFrame(bio_list).to_csv('data/player_biometrics_master.csv', index=False)
    pd.DataFrame(telemetry_list).to_csv('data/net_telemetry_balls.csv', index=False)
    
    print(f"Mock data generated successfully in data/ folder for {len(players_raw)} players.")

if __name__ == "__main__":
    generate_mock_data()
