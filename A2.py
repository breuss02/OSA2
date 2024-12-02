import threading
import queue
import time

class CheeseburgerFactory:
    def __init__(self, num_burgers):
        self.num_burgers = num_burgers
        self.burgers_produced = 0

        # Buffers and semaphores
        self.milk_buffer = queue.Queue(maxsize=9)  # Buffer for milk bottles
        self.cheese_buffer = queue.Queue(maxsize=2)  # Buffer for cheese slices

        # Mutex and semaphores
        self.milk_mutex = threading.Semaphore(1)
        self.cheese_mutex = threading.Semaphore(1)

        self.milk_empty = threading.Semaphore(9)
        self.milk_full = threading.Semaphore(0)
        self.cheese_empty = threading.Semaphore(2)
        self.cheese_full = threading.Semaphore(0)

        # Unique milk ID counter
        self.milk_id_counter = 1
        self.milk_id_lock = threading.Lock()

    def milk_producer(self, producer_id):
        """Produces milk bottles."""
        for _ in range(2 * self.num_burgers):
            self.milk_empty.acquire()
            self.milk_mutex.acquire()
            try:
                with self.milk_id_lock:
                    milk_id = self.milk_id_counter
                    self.milk_id_counter += 1
                self.milk_buffer.put(milk_id)
                print(f"Milk Producer {producer_id} added milk {milk_id}.")
            finally:
                self.milk_mutex.release()
                self.milk_full.release()
            time.sleep(0.1)  # Simulate production delay

    def cheese_producer(self, producer_id):
        """Converts milk bottles into cheese slices."""
        for _ in range(self.num_burgers):
            for _ in range(3):  # Wait for 3 milk bottles
                self.milk_full.acquire()
            self.milk_mutex.acquire()
            try:
                milk_ids = [self.milk_buffer.get() for _ in range(3)]
                for _ in milk_ids:
                    self.milk_empty.release()
                # Ensure uniqueness by sorting milk IDs and including producer ID
                cheese_id = int(''.join(map(str, sorted(milk_ids))) + f"{producer_id}")
            finally:
                self.milk_mutex.release()
            self.cheese_empty.acquire()
            self.cheese_mutex.acquire()
            try:
                self.cheese_buffer.put(cheese_id)
                print(f"Cheese Producer {producer_id} created cheese slice {cheese_id}.")
            finally:
                self.cheese_mutex.release()
                self.cheese_full.release()
            time.sleep(0.1)  # Simulate production delay

    def cheeseburger_producer(self):
        """Assembles cheeseburgers from cheese slices."""
        while self.burgers_produced < self.num_burgers:
            for _ in range(2):  # Wait for 2 cheese slices
                self.cheese_full.acquire()
            self.cheese_mutex.acquire()
            try:
                # Collect 2 cheese slices from the buffer
                cheese_slices = [self.cheese_buffer.get() for _ in range(2)]
                for _ in cheese_slices:
                    self.cheese_empty.release()
                # Sort cheese slices to ensure consistent ID formation
                burger_id = int(''.join(map(str, sorted(cheese_slices))))
                print(f"Cheeseburger Producer created cheeseburger {burger_id}.")
                self.burgers_produced += 1
            finally:
                self.cheese_mutex.release()
            time.sleep(0.1)  # Simulate production delay

def main():
    """Main function to initialize and start threads."""
    while True:
        try:
            num_burgers = int(input("How many burgers do you want? "))
            if num_burgers > 0:
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid integer.")

    factory = CheeseburgerFactory(num_burgers)

    # Create threads
    milk_threads = [threading.Thread(target=factory.milk_producer, args=(i + 1,)) for i in range(3)]
    cheese_threads = [threading.Thread(target=factory.cheese_producer, args=(i + 4,)) for i in range(2)]
    burger_thread = threading.Thread(target=factory.cheeseburger_producer)

    # Start threads
    for thread in milk_threads + cheese_threads + [burger_thread]:
        thread.start()

    # Wait for threads to finish
    for thread in milk_threads + cheese_threads + [burger_thread]:
        thread.join()

    print("All cheeseburgers produced successfully!")

if __name__ == "__main__":
    main()
