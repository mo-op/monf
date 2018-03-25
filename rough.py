my_range=range(1,len(df.index)+1)
 
# The vertival plot is made using the hline function
# I load the seaborn library only to benefit the nice looking feature
import seaborn as sns
plt.hlines(y=my_range, xmin=0, xmax=df['population'], color='skyblue')
plt.plot(df['population'], my_range, "o")
 
# Add titles and axis names
plt.yticks(my_range,df['country'])
plt.title("Population : Countries", loc='left')
plt.xlabel('population')
plt.ylabel('Country')
plt.savefig('/plot.png')