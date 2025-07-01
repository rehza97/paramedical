
import requests
import unittest
import json
from datetime import datetime, timedelta

class StagesParamedicauxAPITester:
    def __init__(self, base_url="https://0f8b0993-6796-42d9-a792-56f605ed229e.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.created_promotions = []
        self.created_services = []

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"Response: {response.json()}")
                except:
                    print(f"Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health(self):
        """Test health check endpoint"""
        return self.run_test("Health Check", "GET", "health", 200)

    def test_create_service(self, nom, places_disponibles, duree_stage_jours):
        """Create a service"""
        data = {
            "nom": nom,
            "places_disponibles": places_disponibles,
            "duree_stage_jours": duree_stage_jours
        }
        success, response = self.run_test(
            f"Create Service: {nom}",
            "POST",
            "services",
            200,
            data=data
        )
        if success and "id" in response:
            self.created_services.append(response["id"])
            return response["id"]
        return None

    def test_get_services(self):
        """Get all services"""
        return self.run_test("Get All Services", "GET", "services", 200)

    def test_create_promotion(self, nom, annee, etudiants):
        """Create a promotion with students"""
        data = {
            "nom": nom,
            "annee": annee,
            "etudiants": etudiants
        }
        success, response = self.run_test(
            f"Create Promotion: {nom}",
            "POST",
            "promotions",
            200,
            data=data
        )
        if success and "id" in response:
            self.created_promotions.append(response["id"])
            return response["id"]
        return None

    def test_get_promotions(self):
        """Get all promotions"""
        return self.run_test("Get All Promotions", "GET", "promotions", 200)

    def test_get_promotion(self, promo_id):
        """Get a specific promotion"""
        return self.run_test(f"Get Promotion {promo_id}", "GET", f"promotions/{promo_id}", 200)

    def test_generate_planning(self, promo_id, date_debut="2025-01-01"):
        """Generate planning for a promotion"""
        return self.run_test(
            f"Generate Planning for Promotion {promo_id}",
            "POST",
            f"plannings/generer/{promo_id}?date_debut={date_debut}",
            200
        )

    def test_get_planning(self, promo_id):
        """Get planning for a promotion"""
        return self.run_test(f"Get Planning for Promotion {promo_id}", "GET", f"plannings/{promo_id}", 200)

    def test_get_student_planning(self, promo_id, etudiant_id):
        """Get planning for a specific student"""
        return self.run_test(
            f"Get Student Planning",
            "GET",
            f"plannings/etudiant/{promo_id}/{etudiant_id}",
            200
        )

    def cleanup(self):
        """Clean up created resources"""
        for promo_id in self.created_promotions:
            self.run_test(f"Delete Promotion {promo_id}", "DELETE", f"promotions/{promo_id}", 200)
        
        for service_id in self.created_services:
            self.run_test(f"Delete Service {service_id}", "DELETE", f"services/{service_id}", 200)

    def print_results(self):
        """Print test results summary"""
        print(f"\n📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        return self.tests_passed == self.tests_run

def generate_test_students(count=15):
    """Generate a list of test students"""
    students = []
    first_names = ["Emma", "Lucas", "Léa", "Hugo", "Chloé", "Louis", "Inès", "Raphaël", "Jade", "Jules", "Manon", "Ethan", "Sarah", "Nathan", "Camille"]
    last_names = ["Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit", "Durand", "Leroy", "Moreau", "Simon", "Michel", "Lefebvre", "Garcia", "David"]
    
    for i in range(min(count, len(first_names))):
        students.append({
            "id": str(i+1),  # Add an ID for each student
            "nom": last_names[i],
            "prenom": first_names[i]
        })
    
    return students

def run_tests():
    tester = StagesParamedicauxAPITester()
    
    # Test 1: Health check
    success, _ = tester.test_health()
    if not success:
        print("❌ Health check failed, stopping tests")
        return False
    
    # Test 2: Create services
    services_data = [
        {"nom": "Cardiologie", "places_disponibles": 5, "duree_stage_jours": 14},
        {"nom": "Urgences", "places_disponibles": 8, "duree_stage_jours": 21},
        {"nom": "Pédiatrie", "places_disponibles": 3, "duree_stage_jours": 10},
        {"nom": "Pneumologie", "places_disponibles": 6, "duree_stage_jours": 15}
    ]
    
    service_ids = []
    for service in services_data:
        service_id = tester.test_create_service(service["nom"], service["places_disponibles"], service["duree_stage_jours"])
        if service_id:
            service_ids.append(service_id)
    
    if len(service_ids) != len(services_data):
        print(f"❌ Failed to create all services, only created {len(service_ids)}/{len(services_data)}")
    
    # Test 3: Get services
    success, services = tester.test_get_services()
    if success:
        print(f"Found {len(services)} services")
    
    # Test 4: Create a promotion with students
    students = generate_test_students(15)
    promo_id = tester.test_create_promotion("Promo 2025", 2025, students)
    
    if not promo_id:
        print("❌ Failed to create promotion, stopping tests")
        return False
    
    # Test 5: Get promotions
    success, promotions = tester.test_get_promotions()
    if success:
        print(f"Found {len(promotions)} promotions")
    
    # Test 6: Get specific promotion
    success, promotion = tester.test_get_promotion(promo_id)
    if success:
        print(f"Retrieved promotion: {promotion['nom']} with {len(promotion['etudiants'])} students")
        # Save first student ID for later testing
        first_student_id = promotion['etudiants'][0]['id'] if promotion['etudiants'] else None
    
    # Test 7: Generate planning
    if len(service_ids) > 0:
        success, planning_result = tester.test_generate_planning(promo_id)
        if success:
            print("Planning generated successfully")
        
        # Test 8: Get planning
        success, planning = tester.test_get_planning(promo_id)
        if success:
            print(f"Retrieved planning with {len(planning['rotations'])} rotations")
            
            # Verify planning integrity
            verify_planning(planning, promotion, services)
        
        # Test 9: Get student planning
        if first_student_id:
            success, student_planning = tester.test_get_student_planning(promo_id, first_student_id)
            if success:
                print(f"Retrieved student planning with {len(student_planning['rotations'])} rotations")
    
    # Test 10: Error cases
    # Try to create a promotion without students
    success, _ = tester.run_test(
        "Create Invalid Promotion (No Students)",
        "POST",
        "promotions",
        400,  # Expecting a 400 Bad Request
        data={"nom": "Invalid Promo", "annee": 2025, "etudiants": []}
    )
    
    # Try to create a service with invalid values
    success, _ = tester.run_test(
        "Create Invalid Service (Negative Values)",
        "POST",
        "services",
        400,  # Expecting a 400 Bad Request
        data={"nom": "Invalid Service", "places_disponibles": -1, "duree_stage_jours": 0}
    )
    
    # Try to generate a planning for a non-existent promotion
    success, _ = tester.run_test(
        "Generate Planning for Non-existent Promotion",
        "POST",
        "plannings/generer/non-existent-id",
        404  # Expecting a 404 Not Found
    )
    
    # Clean up
    # tester.cleanup()
    
    # Print results
    return tester.print_results()

def verify_planning(planning, promotion, services):
    """Verify planning integrity"""
    print("\n🔍 Verifying planning integrity...")
    
    # Get unique students and services in the planning
    students = promotion['etudiants']
    student_ids = set(student['id'] for student in students)
    service_ids = set(service['id'] for service in services)
    
    # Count rotations per student
    student_rotations = {}
    for rotation in planning['rotations']:
        student_id = rotation['etudiant_id']
        if student_id not in student_rotations:
            student_rotations[student_id] = []
        student_rotations[student_id].append(rotation)
    
    # Check if all students have rotations in all services
    all_students_all_services = True
    for student_id in student_ids:
        if student_id not in student_rotations:
            print(f"❌ Student {student_id} has no rotations")
            all_students_all_services = False
            continue
        
        student_services = set(rotation['service_id'] for rotation in student_rotations[student_id])
        if student_services != service_ids:
            print(f"❌ Student {student_id} is missing rotations in some services")
            all_students_all_services = False
    
    if all_students_all_services:
        print("✅ All students have rotations in all services")
    
    # Check date consistency
    date_consistent = True
    for student_id, rotations in student_rotations.items():
        sorted_rotations = sorted(rotations, key=lambda r: r['ordre'])
        for i in range(1, len(sorted_rotations)):
            prev_end = datetime.strptime(sorted_rotations[i-1]['date_fin'], "%Y-%m-%d")
            curr_start = datetime.strptime(sorted_rotations[i]['date_debut'], "%Y-%m-%d")
            if prev_end >= curr_start:
                print(f"❌ Date inconsistency for student {student_id}: rotation {i-1} ends after rotation {i} starts")
                date_consistent = False
    
    if date_consistent:
        print("✅ All rotation dates are consistent")
    
    # Check service capacity
    capacity_respected = True
    # Group rotations by service and date
    service_date_students = {}
    for rotation in planning['rotations']:
        service_id = rotation['service_id']
        date_debut = rotation['date_debut']
        if (service_id, date_debut) not in service_date_students:
            service_date_students[(service_id, date_debut)] = []
        service_date_students[(service_id, date_debut)].append(rotation['etudiant_id'])
    
    # Check if any service exceeds capacity
    for service in services:
        service_id = service['id']
        capacity = service['places_disponibles']
        for (s_id, date), students in service_date_students.items():
            if s_id == service_id and len(students) > capacity:
                print(f"❌ Service {service['nom']} exceeds capacity on {date}: {len(students)}/{capacity}")
                capacity_respected = False
    
    if capacity_respected:
        print("✅ All service capacities are respected")
    
    return all_students_all_services and date_consistent and capacity_respected

if __name__ == "__main__":
    print("🏥 Starting Stages Paramédicaux API Tests 🏥")
    success = run_tests()
    print("\n🏁 Tests completed")
    if success:
        print("✅ All tests passed successfully")
    else:
        print("❌ Some tests failed")