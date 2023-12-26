from urllib.parse import urljoin

# Base URL of the website
base_url = "https://example.com/dir1/dir2/dir3/"

# Relative paths
relative_path1 = "../ab"
relative_path2 = "/../../ab"
relative_path3 = "/ab"

# Combine to form absolute URLs
absolute_url1 = urljoin(base_url, relative_path1)
absolute_url2 = urljoin(base_url, relative_path2)
absolute_url3 = urljoin(base_url, relative_path3)

print(absolute_url1)  # Output will be based on the relative path from the base URL
print(absolute_url2)  # Output: https://example.com/ab
print(absolute_url3)  # Output: https://example.com/ab