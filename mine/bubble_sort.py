def bubble_sort(arr):
    """
    Bubble sort implementation in Python.
    
    Args:
        arr: List of elements to sort
        
    Returns:
        Sorted list
    """
    n = len(arr)
    
    # Traverse through all array elements
    for i in range(n):
        # Last i elements are already in place
        for j in range(0, n - i - 1):
            # Traverse the array from 0 to n-i-1
            # Swap if the element found is greater than the next element
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    
    return arr


# Example usage
if __name__ == "__main__":
    # Test the bubble sort
    test_array = [64, 34, 25, 12, 22, 11, 90]
    print("Original array:", test_array)
    
    sorted_array = bubble_sort(test_array.copy())
    print("Sorted array:", sorted_array)
    
    # Another test with negative numbers
    test_array2 = [-5, 10, 3, -8, 0, 7]
    print("\nOriginal array:", test_array2)
    print("Sorted array:", bubble_sort(test_array2.copy()))
