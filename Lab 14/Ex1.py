import matplotlib.pyplot as plt

x_values = [1, 2, 3, 4, 5]
y_values = [1, 3, 3, 3.5, 4]

# Plot these values
#plt.plot(x_values, y_values)
plt.scatter(x_values, y_values)

# Now add in a second set of values
other_x = [1, 2, 3, 4]
other_y = [2, 4, 6, 8]
plt.plot(other_x, other_y)

# Add in X and Y axis labels and a title
plt.xlabel("X values")
plt.ylabel("Y values")
plt.title("Line and Scatter Plot")


plt.show()