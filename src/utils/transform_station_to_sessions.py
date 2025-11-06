"""
Transform EV Charging Station Data to Charging Sessions

This script transforms static charging station infrastructure data into realistic
temporal charging session data suitable for scheduling algorithms.

Key transformations:
- DC Fast Chargers → Short sessions (15-45 min)
- AC Level 2 → Medium sessions (1-4 hours)
- AC Level 1 → Long sessions (4-8 hours)
- Usage stats → Session frequency
- Availability hours → Time constraints

Author: Generated for AOA Project 1
Date: November 2025
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Tuple, Dict
import os


class StationToSessionTransformer:
    """Transform station infrastructure data to charging session data."""
    
    # Charging duration ranges by charger type (in minutes)
    DURATION_RANGES = {
        'DC Fast Charger': (15, 45),      # Fast charging: 15-45 minutes
        'AC Level 2': (60, 240),          # Level 2: 1-4 hours
        'AC Level 1': (240, 480),         # Level 1: 4-8 hours
    }
    
    # Peak hour multipliers for realistic demand patterns
    PEAK_HOURS = {
        'morning': (7, 9, 1.5),    # 7-9 AM, 1.5x demand
        'lunch': (12, 14, 1.3),    # 12-2 PM, 1.3x demand
        'evening': (17, 20, 2.0),  # 5-8 PM, 2.0x demand
    }
    
    def __init__(self, seed: int = 42):
        """
        Initialize transformer.
        
        Args:
            seed: Random seed for reproducibility
        """
        self.rng = np.random.RandomState(seed)
        self.session_counter = 0
        
    def parse_availability(self, availability_str: str) -> Tuple[float, float]:
        """
        Parse availability string to start/end times in minutes since midnight.
        
        Args:
            availability_str: String like "9:00-18:00" or "24/7"
            
        Returns:
            (start_minutes, end_minutes) tuple
        """
        if availability_str == '24/7':
            return (0.0, 1440.0)  # Full day
        
        try:
            start_str, end_str = availability_str.split('-')
            start_hour, start_min = map(int, start_str.split(':'))
            end_hour, end_min = map(int, end_str.split(':'))
            
            start_minutes = start_hour * 60 + start_min
            end_minutes = end_hour * 60 + end_min
            
            return (float(start_minutes), float(end_minutes))
        except:
            # Default to 9 AM - 6 PM if parsing fails
            return (540.0, 1080.0)
    
    def get_peak_multiplier(self, time_minutes: float) -> float:
        """
        Get demand multiplier based on time of day.
        
        Args:
            time_minutes: Time in minutes since midnight
            
        Returns:
            Multiplier value (1.0 = normal, >1.0 = peak)
        """
        hour = time_minutes / 60.0
        
        for peak_name, (start_h, end_h, multiplier) in self.PEAK_HOURS.items():
            if start_h <= hour < end_h:
                return multiplier
        
        return 1.0  # Normal hours
    
    def generate_session_duration(self, charger_type: str, capacity_kw: float) -> float:
        """
        Generate realistic session duration based on charger type and capacity.
        
        Args:
            charger_type: Type of charger
            capacity_kw: Charging capacity in kW
            
        Returns:
            Duration in minutes
        """
        min_dur, max_dur = self.DURATION_RANGES.get(
            charger_type, 
            (60, 180)  # Default to Level 2 range
        )
        
        # Adjust based on capacity (higher capacity = potentially shorter sessions)
        if capacity_kw >= 150:
            # High capacity: bias toward shorter end
            duration = self.rng.triangular(min_dur, min_dur, max_dur)
        elif capacity_kw <= 50:
            # Low capacity: bias toward longer end
            duration = self.rng.triangular(min_dur, max_dur, max_dur)
        else:
            # Medium capacity: uniform distribution
            duration = self.rng.uniform(min_dur, max_dur)
        
        return duration
    
    def generate_sessions_for_station(
        self, 
        station: pd.Series,
        num_days: int = 7
    ) -> List[Dict]:
        """
        Generate charging sessions for a single station over multiple days.
        
        Args:
            station: Row from station DataFrame
            num_days: Number of days to simulate
            
        Returns:
            List of session dictionaries
        """
        sessions = []
        
        # Parse station attributes
        station_id = station['Station ID']
        charger_type = station['Charger Type']
        capacity_kw = station['Charging Capacity (kW)']
        avg_users_per_day = station['Usage Stats (avg users/day)']
        start_time, end_time = self.parse_availability(station['Availability'])
        
        # Calculate operational hours per day
        operational_hours = (end_time - start_time) / 60.0
        
        for day in range(num_days):
            # Daily base time offset (in minutes)
            day_offset = day * 1440  # 1440 minutes per day
            
            # Calculate number of sessions for this day
            # Add some randomness around the average
            num_sessions = max(1, int(self.rng.poisson(avg_users_per_day)))
            
            # Track occupied time slots to avoid overlaps at same station
            occupied_slots = []
            
            for _ in range(num_sessions):
                # Generate session duration
                duration = self.generate_session_duration(charger_type, capacity_kw)
                
                # Try to find non-overlapping time slot (up to 10 attempts)
                for attempt in range(10):
                    # Generate arrival time within availability window
                    # Use exponential inter-arrival for realistic spacing
                    if len(occupied_slots) == 0:
                        arrival = start_time + self.rng.uniform(0, operational_hours * 60)
                    else:
                        # Base on last session with some gap
                        last_end = max(end for _, end in occupied_slots)
                        if last_end >= end_time - duration:
                            break  # No more room today
                        arrival = last_end + self.rng.exponential(30)  # 30 min avg gap
                    
                    # Apply peak hour multiplier (higher chance during peaks)
                    peak_mult = self.get_peak_multiplier(arrival)
                    if self.rng.random() > 1.0 / peak_mult:
                        continue  # Skip this slot during off-peak
                    
                    # Ensure session fits within availability
                    if arrival + duration > end_time:
                        continue
                    
                    session_start = day_offset + arrival
                    session_end = day_offset + arrival + duration
                    
                    # Check for overlaps
                    overlaps = any(
                        not (session_end <= occ_start or session_start >= occ_end)
                        for occ_start, occ_end in occupied_slots
                    )
                    
                    if not overlaps:
                        # Success! Create session
                        self.session_counter += 1
                        
                        # Calculate energy delivered (capacity * duration / 60 * efficiency)
                        efficiency = 0.85  # 85% charging efficiency
                        energy_kwh = (capacity_kw * (duration / 60.0) * efficiency)
                        
                        session = {
                            'session_id': f"SES{self.session_counter:06d}",
                            'start_time': round(session_start, 2),
                            'finish_time': round(session_end, 2),
                            'user_id': f"user_{station_id}_{self.session_counter % 1000}",
                            'energy_kwh': round(energy_kwh, 2),
                            'station_id': station_id,
                            'charger_type': charger_type,
                            'capacity_kw': capacity_kw,
                            'cost_per_kwh': station['Cost (USD/kWh)'],
                            'day': day,
                        }
                        
                        sessions.append(session)
                        occupied_slots.append((session_start, session_end))
                        break
        
        return sessions
    
    def transform_dataset(
        self,
        station_data_path: str,
        output_path: str,
        num_days: int = 7,
        max_stations: int = None,
        sample_random: bool = True
    ) -> pd.DataFrame:
        """
        Transform entire station dataset to session data.
        
        Args:
            station_data_path: Path to station CSV file
            output_path: Path to save session CSV file
            num_days: Number of days to simulate
            max_stations: Limit number of stations (None = all)
            sample_random: If limiting stations, sample randomly vs first N
            
        Returns:
            DataFrame of generated sessions
        """
        print(f"📂 Loading station data from: {station_data_path}")
        stations_df = pd.read_csv(station_data_path)
        print(f"   Found {len(stations_df)} stations")
        
        # Optionally limit stations for faster processing
        if max_stations and max_stations < len(stations_df):
            if sample_random:
                stations_df = stations_df.sample(n=max_stations, random_state=42)
                print(f"   Randomly sampled {max_stations} stations")
            else:
                stations_df = stations_df.head(max_stations)
                print(f"   Using first {max_stations} stations")
        
        print(f"\n🔄 Generating sessions for {num_days} days...")
        all_sessions = []
        
        for idx, station in stations_df.iterrows():
            sessions = self.generate_sessions_for_station(station, num_days)
            all_sessions.extend(sessions)
            
            if (idx + 1) % 500 == 0:
                print(f"   Processed {idx + 1}/{len(stations_df)} stations... "
                      f"({len(all_sessions)} sessions so far)")
        
        print(f"\n✅ Generated {len(all_sessions)} total sessions")
        
        # Create DataFrame
        sessions_df = pd.DataFrame(all_sessions)
        
        # Sort by start time for better visualization
        sessions_df = sessions_df.sort_values('start_time').reset_index(drop=True)
        
        # Save to CSV
        print(f"\n💾 Saving to: {output_path}")
        sessions_df.to_csv(output_path, index=False)
        
        # Print statistics
        self._print_statistics(sessions_df, stations_df)
        
        return sessions_df
    
    def _print_statistics(self, sessions_df: pd.DataFrame, stations_df: pd.DataFrame):
        """Print helpful statistics about generated data."""
        print("\n" + "="*70)
        print("📊 GENERATED SESSION STATISTICS")
        print("="*70)
        
        print(f"\n🔢 Basic Stats:")
        print(f"   Total sessions: {len(sessions_df)}")
        print(f"   From {len(stations_df)} stations")
        print(f"   Sessions per station (avg): {len(sessions_df)/len(stations_df):.1f}")
        
        print(f"\n⚡ By Charger Type:")
        for charger_type in sessions_df['charger_type'].unique():
            count = len(sessions_df[sessions_df['charger_type'] == charger_type])
            avg_duration = sessions_df[sessions_df['charger_type'] == charger_type]['finish_time'] - \
                          sessions_df[sessions_df['charger_type'] == charger_type]['start_time']
            print(f"   {charger_type:20s}: {count:6d} sessions, "
                  f"avg duration {avg_duration.mean():.1f} min")
        
        print(f"\n⏱️  Duration Stats (minutes):")
        durations = sessions_df['finish_time'] - sessions_df['start_time']
        print(f"   Min:    {durations.min():.1f}")
        print(f"   Max:    {durations.max():.1f}")
        print(f"   Mean:   {durations.mean():.1f}")
        print(f"   Median: {durations.median():.1f}")
        
        print(f"\n🔋 Energy Stats (kWh):")
        print(f"   Min:    {sessions_df['energy_kwh'].min():.2f}")
        print(f"   Max:    {sessions_df['energy_kwh'].max():.2f}")
        print(f"   Mean:   {sessions_df['energy_kwh'].mean():.2f}")
        print(f"   Total:  {sessions_df['energy_kwh'].sum():.2f}")
        
        print(f"\n💰 Cost Stats (USD):")
        total_cost = (sessions_df['energy_kwh'] * sessions_df['cost_per_kwh']).sum()
        avg_cost = (sessions_df['energy_kwh'] * sessions_df['cost_per_kwh']).mean()
        print(f"   Total revenue: ${total_cost:.2f}")
        print(f"   Avg per session: ${avg_cost:.2f}")
        
        print(f"\n📅 Temporal Distribution:")
        for day in sorted(sessions_df['day'].unique()):
            count = len(sessions_df[sessions_df['day'] == day])
            print(f"   Day {day}: {count} sessions")
        
        print("\n" + "="*70)


def create_minimal_session_file(
    sessions_df: pd.DataFrame,
    output_path: str
):
    """
    Create a minimal CSV with only fields required by the algorithm.
    
    Args:
        sessions_df: Full session DataFrame
        output_path: Path to save minimal CSV
    """
    minimal_df = sessions_df[['session_id', 'start_time', 'finish_time', 
                               'user_id', 'energy_kwh']].copy()
    minimal_df.to_csv(output_path, index=False)
    print(f"✅ Minimal session file saved to: {output_path}")
    print(f"   (Only required columns: session_id, start_time, finish_time, user_id, energy_kwh)")


def main():
    """Main execution function."""
    print("\n" + "="*70)
    print("🔌 EV CHARGING STATION → SESSION TRANSFORMER")
    print("="*70)
    
    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
    
    station_file = os.path.join(
        project_root, 
        'experiments', 'data', 'detailed_ev_charging_stations.csv'
    )
    session_file_full = os.path.join(
        project_root,
        'experiments', 'data', 'ev_charging_sessions_full.csv'
    )
    session_file_minimal = os.path.join(
        project_root,
        'experiments', 'data', 'ev_charging_real.csv'
    )
    
    # Check if input exists
    if not os.path.exists(station_file):
        print(f"❌ Error: Station data file not found at:")
        print(f"   {station_file}")
        return
    
    # Create transformer
    transformer = StationToSessionTransformer(seed=42)
    
    # Transform data
    # Using subset for manageable dataset size (500 stations × 7 days)
    sessions_df = transformer.transform_dataset(
        station_data_path=station_file,
        output_path=session_file_full,
        num_days=7,
        max_stations=500,  # Limit for reasonable runtime
        sample_random=True
    )
    
    # Create minimal version for algorithm
    create_minimal_session_file(sessions_df, session_file_minimal)
    
    print("\n" + "="*70)
    print("✅ TRANSFORMATION COMPLETE!")
    print("="*70)
    print(f"\n📁 Output files created:")
    print(f"   1. Full data:    {session_file_full}")
    print(f"      (Includes all attributes for analysis)")
    print(f"   2. Minimal data: {session_file_minimal}")
    print(f"      (Only required fields for algorithm)")
    
    print(f"\n🚀 Next steps:")
    print(f"   1. Run: python src/greedy/experiment.py")
    print(f"      (Will automatically load {os.path.basename(session_file_minimal)})")
    print(f"   2. Check results in experiments/results/")
    print(f"   3. Review visualizations generated")
    
    print("\n" + "="*70)


if __name__ == '__main__':
    main()
