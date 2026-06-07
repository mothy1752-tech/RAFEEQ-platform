from datetime import datetime, timedelta
from database import Database
import json

class TransportationManager:
    """
    Manage accessible transportation services for RAFEEQ platform
    """
    
    def __init__(self):
        self.db = Database()
        self.base_rate_per_km = 2.5  # SAR per kilometer
    
    def book_ride(self, user_id, pickup, dropoff, pickup_time, booking_type, needs):
        """
        Book accessible transportation
        
        Args:
            user_id: User ID
            pickup: Pickup location
            dropoff: Dropoff location
            pickup_time: Datetime for pickup
            booking_type: Type of booking (interview, work_commute, training, other)
            needs: Dictionary with special requirements
        
        Returns:
            Success status and booking details or error message
        """
        conn = self.db.connect()
        if not conn:
            return False, "Database connection failed"
        
        cursor = conn.cursor()
        
        try:
            # Find available vehicle
            service_id = self._find_available_vehicle(
                needs.get('city'),
                needs.get('vehicle_requirements', {}),
                pickup_time
            )
            
            if not service_id:
                return False, "No available vehicles matching your requirements"
            
            # Create booking
            cursor.execute('''
                INSERT INTO transportation_bookings (
                    user_id, service_id, booking_type, pickup_location,
                    dropoff_location, pickup_time, needs_companion,
                    special_requirements, status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pending')
            ''', (
                user_id,
                service_id,
                booking_type,
                pickup,
                dropoff,
                pickup_time,
                needs.get('needs_companion', False),
                json.dumps(needs.get('special_requirements', {}))
            ))
            
            booking_id = cursor.lastrowid
            conn.commit()
            
            # Get booking details
            booking_details = self.get_booking_details(booking_id)
            
            cursor.close()
            conn.close()
            
            return True, booking_details
            
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            return False, str(e)
    
    def _find_available_vehicle(self, city, requirements, pickup_time):
        """
        Find vehicles matching accessibility needs
        """
        conn = self.db.connect()
        if not conn:
            return None
        
        cursor = conn.cursor()
        
        try:
            # Build query based on requirements
            query = '''
                SELECT service_id FROM transportation_services
                WHERE city = %s AND availability_status = 'available'
            '''
            params = [city]
            
            # Add vehicle type requirement
            if requirements.get('vehicle_type'):
                query += ' AND vehicle_type = %s'
                params.append(requirements['vehicle_type'])
            
            # Add wheelchair lift requirement
            if requirements.get('needs_wheelchair_lift'):
                query += ' AND has_wheelchair_lift = TRUE'
            
            # Add ramp requirement
            if requirements.get('needs_ramp'):
                query += ' AND has_ramp = TRUE'
            
            # Add companion requirement
            if requirements.get('needs_companion'):
                query += ' AND can_accommodate_companion = TRUE'
            
            # Add trained driver requirement
            if requirements.get('needs_trained_driver'):
                query += ' AND driver_trained = TRUE'
            
            query += ' LIMIT 1'
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if result:
                return result['service_id']
            return None
            
        except Exception as e:
            cursor.close()
            conn.close()
            return None
    
    def find_available_vehicles(self, city, requirements):
        """
        Find all vehicles matching accessibility needs
        """
        conn = self.db.connect()
        if not conn:
            return []
        
        cursor = conn.cursor()
        
        try:
            query = '''
                SELECT * FROM transportation_services
                WHERE city = %s AND availability_status = 'available'
            '''
            params = [city]
            
            if requirements.get('vehicle_type'):
                query += ' AND vehicle_type = %s'
                params.append(requirements['vehicle_type'])
            
            if requirements.get('needs_wheelchair_lift'):
                query += ' AND has_wheelchair_lift = TRUE'
            
            if requirements.get('needs_ramp'):
                query += ' AND has_ramp = TRUE'
            
            if requirements.get('needs_companion'):
                query += ' AND can_accommodate_companion = TRUE'
            
            cursor.execute(query, params)
            vehicles = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return vehicles
            
        except Exception as e:
            cursor.close()
            conn.close()
            return []
    
    def track_ride(self, booking_id):
        """
        Real-time ride tracking
        """
        booking = self.get_booking_details(booking_id)
        
        if not booking:
            return None
        
        # Calculate estimated time and status
        tracking_info = {
            'booking_id': booking_id,
            'status': booking['status'],
            'pickup_location': booking['pickup_location'],
            'dropoff_location': booking['dropoff_location'],
            'pickup_time': booking['pickup_time'],
            'service_name': booking.get('service_name', ''),
            'vehicle_type': booking.get('vehicle_type', ''),
            'driver_phone': booking.get('contact_phone', '')
        }
        
        # Add estimated arrival time based on status
        if booking['status'] == 'confirmed':
            tracking_info['estimated_arrival'] = booking['pickup_time']
            tracking_info['message'] = 'Driver confirmed. Vehicle will arrive at scheduled time.'
        elif booking['status'] == 'in_progress':
            tracking_info['message'] = 'Ride in progress. Heading to destination.'
        elif booking['status'] == 'completed':
            tracking_info['message'] = 'Ride completed. Thank you for using RAFEEQ Transportation.'
        elif booking['status'] == 'cancelled':
            tracking_info['message'] = 'Booking cancelled.'
        else:
            tracking_info['message'] = 'Waiting for driver confirmation.'
        
        return tracking_info
    
    def get_booking_details(self, booking_id):
        """
        Get detailed booking information
        """
        conn = self.db.connect()
        if not conn:
            return None
        
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    tb.*,
                    ts.service_name,
                    ts.vehicle_type,
                    ts.contact_phone,
                    ts.pricing_per_km
                FROM transportation_bookings tb
                JOIN transportation_services ts ON tb.service_id = ts.service_id
                WHERE tb.booking_id = %s
            ''', (booking_id,))
            
            booking = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return booking
            
        except Exception as e:
            cursor.close()
            conn.close()
            return None
    
    def calculate_cost(self, distance_km, vehicle_type):
        """
        Calculate ride cost based on distance and vehicle type
        """
        base_cost = distance_km * self.base_rate_per_km
        
        # Vehicle type multipliers
        multipliers = {
            'wheelchair_van': 1.5,
            'accessible_sedan': 1.2,
            'standard_accessible': 1.0
        }
        
        multiplier = multipliers.get(vehicle_type, 1.0)
        total_cost = base_cost * multiplier
        
        # Minimum fare
        minimum_fare = 15.0  # SAR
        
        return max(total_cost, minimum_fare)
    
    def get_user_booking_history(self, user_id, limit=10):
        """
        Get user's transportation booking history
        """
        conn = self.db.connect()
        if not conn:
            return []
        
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    tb.*,
                    ts.service_name,
                    ts.vehicle_type
                FROM transportation_bookings tb
                JOIN transportation_services ts ON tb.service_id = ts.service_id
                WHERE tb.user_id = %s
                ORDER BY tb.created_at DESC
                LIMIT %s
            ''', (user_id, limit))
            
            bookings = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return bookings
            
        except Exception as e:
            cursor.close()
            conn.close()
            return []
    
    def update_booking_status(self, booking_id, new_status):
        """
        Update booking status
        """
        conn = self.db.connect()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE transportation_bookings
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE booking_id = %s
            ''', (new_status, booking_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            return False
    
    def cancel_booking(self, booking_id, user_id):
        """
        Cancel a booking
        """
        # Verify booking belongs to user
        booking = self.get_booking_details(booking_id)
        
        if not booking or booking['user_id'] != user_id:
            return False, "Booking not found or unauthorized"
        
        if booking['status'] in ['completed', 'cancelled']:
            return False, "Cannot cancel completed or already cancelled booking"
        
        # Update status to cancelled
        success = self.update_booking_status(booking_id, 'cancelled')
        
        if success:
            return True, "Booking cancelled successfully"
        else:
            return False, "Failed to cancel booking"
    
    def add_transportation_service(self, service_data):
        """
        Add a new transportation service (Admin function)
        """
        conn = self.db.connect()
        if not conn:
            return False, "Database connection failed"
        
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO transportation_services (
                    service_name, city, vehicle_type, has_wheelchair_lift,
                    has_ramp, can_accommodate_companion, driver_trained,
                    contact_phone, pricing_per_km, availability_status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                service_data['service_name'],
                service_data['city'],
                service_data['vehicle_type'],
                service_data.get('has_wheelchair_lift', False),
                service_data.get('has_ramp', False),
                service_data.get('can_accommodate_companion', False),
                service_data.get('driver_trained', False),
                service_data['contact_phone'],
                service_data.get('pricing_per_km', self.base_rate_per_km),
                'available'
            ))
            
            service_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            conn.close()
            
            return True, service_id
            
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            return False, str(e)
