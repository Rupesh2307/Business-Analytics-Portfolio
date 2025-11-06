## ── Attaching core tidyverse packages ──────────────────────── tidyverse 2.0.0 ──
## ✔ dplyr     1.1.4     ✔ readr     2.1.5
## ✔ forcats   1.0.0     ✔ stringr   1.5.1
## ✔ ggplot2   3.5.2     ✔ tibble    3.2.1
## ✔ lubridate 1.9.4     ✔ tidyr     1.3.1
## ✔ purrr     1.0.4     
## ── Conflicts ────────────────────────────────────────── tidyverse_conflicts() ──
## ✖ dplyr::filter() masks stats::filter()
## ✖ dplyr::lag()    masks stats::lag()
## ℹ Use the conflicted package (<http://conflicted.r-lib.org/>) to force all conflicts to become errors
library(cluster)
## Warning: package 'cluster' was built under R version 4.4.3
library(factoextra)
## Warning: package 'factoextra' was built under R version 4.4.3
## Welcome! Want to learn more? See two factoextra-related books at https://goo.gl/ve3WBa
library(NbClust)
library(flexclust)
## Warning: package 'flexclust' was built under R version 4.4.3
library(kableExtra)
## Warning: package 'kableExtra' was built under R version 4.4.3
## 
## Attaching package: 'kableExtra'
## 
## The following object is masked from 'package:dplyr':
## 
##     group_rows
# Task 1: Read and inspect the dataset
retailer <- read.csv("retailer.csv")

# View structure of the dataset
str(retailer)
## 'data.frame':    200 obs. of  9 variables:
##  $ respondent_id     : int  1 2 3 4 5 6 7 8 9 10 ...
##  $ variety_of_choice : int  8 6 6 8 4 8 7 7 10 8 ...
##  $ electronics       : int  3 3 1 3 6 4 2 5 7 4 ...
##  $ furniture         : int  6 1 2 3 3 3 2 3 5 0 ...
##  $ quality_of_service: int  3 4 4 4 4 5 2 2 1 4 ...
##  $ low_prices        : int  2 7 9 8 2 10 8 2 5 9 ...
##  $ return_policy     : int  2 1 6 7 5 6 7 3 4 1 ...
##  $ income            : int  16 22 18 18 35 13 22 19 14 16 ...
##  $ age               : int  28 27 22 29 51 24 27 26 27 28 ...
# Get basic summary statistics
summary(retailer)
##  respondent_id    variety_of_choice  electronics      furniture   
##  Min.   :  1.00   Min.   : 4.000    Min.   : 1.00   Min.   :0.00  
##  1st Qu.: 50.75   1st Qu.: 6.000    1st Qu.: 3.00   1st Qu.:1.00  
##  Median :100.50   Median : 8.000    Median : 4.50   Median :2.00  
##  Mean   :100.50   Mean   : 7.565    Mean   : 4.45   Mean   :3.27  
##  3rd Qu.:150.25   3rd Qu.:10.000    3rd Qu.: 6.00   3rd Qu.:6.00  
##  Max.   :200.00   Max.   :10.000    Max.   :10.00   Max.   :7.00  
##  quality_of_service   low_prices     return_policy       income     
##  Min.   :1.00       Min.   : 1.000   Min.   : 1.00   Min.   :13.00  
##  1st Qu.:2.00       1st Qu.: 2.000   1st Qu.: 3.00   1st Qu.:15.00  
##  Median :3.00       Median : 5.000   Median : 4.00   Median :19.50  
##  Mean   :3.53       Mean   : 4.795   Mean   : 4.25   Mean   :32.17  
##  3rd Qu.:4.00       3rd Qu.: 7.000   3rd Qu.: 6.00   3rd Qu.:54.25  
##  Max.   :9.00       Max.   :10.000   Max.   :10.00   Max.   :95.00  
##       age       
##  Min.   :21.00  
##  1st Qu.:24.00  
##  Median :27.00  
##  Mean   :32.52  
##  3rd Qu.:38.00  
##  Max.   :68.00
# Task 2: Normalise the data (z-scores), exclude respondent_id
data_for_normalisation <- retailer %>%
  select(-respondent_id)

normalized_data <- scale(data_for_normalisation)

# Find smallest minimum value and its variable
min_vals <- apply(normalized_data, 2, min)
min_var <- names(which.min(min_vals))

# Find largest maximum value and its variable
max_vals <- apply(normalized_data, 2, max)
max_var <- names(which.max(max_vals))

# Display results
cat("Variable with the smallest minimum value:", min_var, "with value", round(min(min_vals), 2), "\n")
## Variable with the smallest minimum value: electronics with value -1.78
cat("Variable with the largest maximum value:", max_var, "with value", round(max(max_vals), 2), "\n")
## Variable with the largest maximum value: age with value 2.99
# Task 3: Select only store attributes
store_attributes <- retailer %>%
  select(variety_of_choice, electronics, furniture,
         quality_of_service, low_prices, return_policy)

# Normalise using z-score standardisation
store_attributes_scaled <- scale(store_attributes)

# Optional: Check result
summary(store_attributes_scaled)
##  variety_of_choice  electronics         furniture       quality_of_service
##  Min.   :-1.7723   Min.   :-1.77534   Min.   :-1.3775   Min.   :-1.0922   
##  1st Qu.:-0.7780   1st Qu.:-0.74616   1st Qu.:-0.9562   1st Qu.:-0.6605   
##  Median : 0.2163   Median : 0.02573   Median :-0.5350   Median :-0.2288   
##  Mean   : 0.0000   Mean   : 0.00000   Mean   : 0.0000   Mean   : 0.0000   
##  3rd Qu.: 1.2106   3rd Qu.: 0.79762   3rd Qu.: 1.1500   3rd Qu.: 0.2029   
##  Max.   : 1.2106   Max.   : 2.85598   Max.   : 1.5713   Max.   : 2.3614   
##    low_prices      return_policy    
##  Min.   :-1.4995   Min.   :-1.5861  
##  1st Qu.:-1.1044   1st Qu.:-0.6100  
##  Median : 0.0810   Median :-0.1220  
##  Mean   : 0.0000   Mean   : 0.0000  
##  3rd Qu.: 0.8713   3rd Qu.: 0.8541  
##  Max.   : 2.0567   Max.   : 2.8062
# Task 4: Calculate Euclidean distance
# Compute Euclidean distance matrix using proxy package (alternative to dist)
if (!require(proxy)) install.packages("proxy")
## Loading required package: proxy
## Warning: package 'proxy' was built under R version 4.4.3
## 
## Attaching package: 'proxy'
## The following objects are masked from 'package:stats':
## 
##     as.dist, dist
## The following object is masked from 'package:base':
## 
##     as.matrix
library(proxy)

# Calculate distance matrix
dist_matrix <- proxy::dist(store_attributes_scaled, method = "Euclidean")

# Convert to matrix and display first 5 rows and columns
head(as.matrix(dist_matrix)[, 1:5], 5)
##          1        2        3        4        5
## 1 0.000000 3.122933 4.066279 3.654938 3.203876
## 2 3.122933 0.000000 2.795657 3.229408 3.434497
## 3 4.066279 2.795657 0.000000 1.618520 3.959120
## 4 3.654938 3.229408 1.618520 0.000000 3.593200
## 5 3.203876 3.434497 3.959120 3.593200 0.000000
# Task 5: RNGkind(kind = "Mersenne-Twister", normal.kind = "Inversion")
set.seed(123)
cat("Seed set to 123 for reproducibility.\n")
## Seed set to 123 for reproducibility.
set.seed(123)
# Task 6: Hierarchical clustering with ward.D2 method
# Hierarchical clustering using ward.D2 on normalised data
distance_matrix <- dist(normalized_data, method = "euclidean")
hc_ward <- hclust(distance_matrix, method = "ward.D2")

# Display the structure of the result
str(hc_ward)
## List of 7
##  $ merge      : int [1:199, 1:2] -16 -50 -78 -84 -99 -15 -102 -18 -19 -89 ...
##  $ height     : num [1:199] 0 0 0 0.0441 0.0441 ...
##  $ order      : int [1:200] 45 160 76 33 53 30 60 73 65 11 ...
##  $ labels     : NULL
##  $ method     : chr "ward.D2"
##  $ call       : language hclust(d = distance_matrix, method = "ward.D2")
##  $ dist.method: chr "Euclidean"
##  - attr(*, "class")= chr "hclust"
# Task 7 : Plot the dendrogram from hierarchical clustering
plot(hc_ward,
     labels = FALSE,             # Do not show labels for clarity
     main = "Hierarchical Clustering Dendrogram (ward.D2)",
     xlab = "",
     sub = "",
     hang = -1,                  # Ensures all leaf nodes align at the bottom
     cex = 0.6)                  # Controls the size of axis text
rect.hclust(hc_ward, k = 3, border = "red")


# Task 8: Highlight 3 clusters on dendrogram and assign clusters

# Plot the hierarchical clustering dendrogram
plot(hc_ward, labels = FALSE, main = "Hierarchical Clustering Dendrogram (ward.D2)")

# Draw rectangles to highlight the 3 clusters
rect.hclust(hc_ward, k = 3, border = "red")


# Assign clusters to data points based on cutting dendrogram at k = 3
clusters_3 <- cutree(hc_ward, k = 3)

# Print the size of each cluster
cluster_sizes <- table(clusters_3)
print(cluster_sizes)
## clusters_3
##  1  2  3 
## 94 60 46
# Task 9: Count observations in each cluster (3-cluster solution)

cluster_sizes_3 <- table(clusters_3)
print(cluster_sizes_3)
## clusters_3
##  1  2  3 
## 94 60 46
# Task 10: K-means clustering on normalized store attributes with 3 clusters
set.seed(123)

kmeans_3 <- kmeans(store_attributes_scaled, centers = 3, iter.max = 1000, nstart = 100)

# Number of observations assigned to each cluster
cluster_sizes <- table(kmeans_3$cluster)
print(cluster_sizes)
## 
##  1  2  3 
## 60 46 94
# Task 11: Assign 4 clusters from hierarchical clustering
clusters_4 <- cutree(hc_ward, k = 4)

# Count observations per cluster
table(clusters_4)
## clusters_4
##  1  2  3  4 
## 65 60 46 29
# Optionally, highlight clusters on dendrogram
plot(hc_ward, labels = FALSE, main = "Hierarchical Clustering Dendrogram - 4 Clusters")
rect.hclust(hc_ward, k = 4, border = "blue")


# Task 12: K-means clustering with 4 clusters
set.seed(123)

kmeans_4 <- kmeans(store_attributes_scaled, centers = 4, iter.max = 1000, nstart = 100)

# Count observations per cluster
table(kmeans_4$cluster)
## 
##  1  2  3  4 
## 17 60 29 94
#Task 13 : 
# Run NbClust
nb <- NbClust(data = store_attributes_scaled, 
              distance = "euclidean", 
              min.nc = 2, 
              max.nc = 6, 
              method = "ward.D2")


## *** : The Hubert index is a graphical method of determining the number of clusters.
##                 In the plot of Hubert index, we seek a significant knee that corresponds to a 
##                 significant increase of the value of the measure i.e the significant peak in Hubert
##                 index second differences plot. 
## 


## *** : The D index is a graphical method of determining the number of clusters. 
##                 In the plot of D index, we seek a significant knee (the significant peak in Dindex
##                 second differences plot) that corresponds to a significant increase of the value of
##                 the measure. 
##  
## ******************************************************************* 
## * Among all indices:                                                
## * 1 proposed 2 as the best number of clusters 
## * 12 proposed 3 as the best number of clusters 
## * 5 proposed 4 as the best number of clusters 
## * 1 proposed 5 as the best number of clusters 
## * 2 proposed 6 as the best number of clusters 
## 
##                    ***** Conclusion *****                            
##  
## * According to the majority rule, the best number of clusters is  3 
##  
##  
## *******************************************************************
# Extract the best number(s) of clusters
best_nc <- nb$Best.nc[1, ]  # First row contains suggested cluster numbers by different criteria

# Print all suggested best cluster numbers
print(best_nc)
##         KL         CH   Hartigan        CCC      Scott    Marriot     TrCovW 
##          3          3          3          6          3          3          3 
##     TraceW   Friedman      Rubin     Cindex         DB Silhouette       Duda 
##          3          3          3          3          4          4         NA 
##   PseudoT2      Beale  Ratkowsky       Ball PtBiserial       Frey    McClain 
##         NA          4          3          3          4          1          2 
##       Dunn     Hubert    SDindex     Dindex       SDbw 
##          5          0          4          0          6
# Summary: how many times each number of clusters was recommended
table(best_nc)
## best_nc
##  0  1  2  3  4  5  6 
##  2  1  1 12  5  1  2
library(dplyr)
library(tidyr)
library(ggplot2)

# Assuming:
# - `store_attributes_scaled` is your scaled data matrix (numeric)
# - `clusters_3` is a vector with cluster assignments (length = number of rows)

# Step 1: Create a dataframe from scaled data and add cluster labels
df_scaled <- as.data.frame(store_attributes_scaled)
df_scaled$cluster <- factor(clusters_3)  # Convert to factor for grouping

# Step 2: Calculate mean per attribute per cluster
cluster_means <- df_scaled %>%
  group_by(cluster) %>%
  summarise(across(everything(), mean)) %>%
  pivot_longer(-cluster, names_to = "attribute", values_to = "mean_value")

# Step 3: Plot cluster profiles using ggplot
ggplot(cluster_means, aes(x = attribute, y = mean_value, group = cluster, color = cluster)) +
  geom_line(size = 1.2) +
  geom_point(size = 3) +
  theme_minimal() +
  labs(title = "Cluster Profiles (3 Clusters)",
       x = "Store Attribute",
       y = "Mean (Z-score)") +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))
## Warning: Using `size` aesthetic for lines was deprecated in ggplot2 3.4.0.
## ℹ Please use `linewidth` instead.
## This warning is displayed once every 8 hours.
## Call `lifecycle::last_lifecycle_warnings()` to see where this warning was
## generated.


#task 14 : 
# Add cluster assignments to original data
retailer_with_clusters <- retailer %>%
  mutate(Cluster = kmeans_3$cluster)

# Group by cluster and compute mean age and income
retailer_with_clusters %>%
  group_by(Cluster) %>%
  summarise(mean_age = mean(age, na.rm = TRUE),
            mean_income = mean(income, na.rm = TRUE)) %>%
  kable(caption = "Average Age and Income per Cluster") %>%
  kable_styling(full_width = FALSE, position = "left")
Average Age and Income per Cluster
Cluster	mean_age	mean_income
1	25.53333	19.05000
2	43.39130	51.36957
3	31.64894	31.14894
#Task 15
# Load necessary library
library(ggplot2)

# Create a data frame with cluster-level data
ge_data <- data.frame(
  Cluster = c("Cluster 1", "Cluster 2", "Cluster 3"),
  Income = c(19.0, 51.4, 31.1),
  Age = c(25.5, 43.4, 31.6),
  BusinessStrength = c(2.5, 4.0, 3.2)
)

# Calculate Market Attractiveness as the average of Income and Age
ge_data$MarketAttractiveness <- rowMeans(ge_data[, c("Income", "Age")])

# Plot the GE Matrix
ggplot(ge_data, aes(x = MarketAttractiveness, y = BusinessStrength, label = Cluster)) +
  geom_point(size = 4, color = "steelblue") +
  geom_text(vjust = -1, hjust = 0.5, size = 4) +
  geom_vline(xintercept = quantile(ge_data$MarketAttractiveness, probs = c(1/3, 2/3)), linetype = "dashed", color = "gray") +
  geom_hline(yintercept = quantile(ge_data$BusinessStrength, probs = c(1/3, 2/3)), linetype = "dashed", color = "gray") +
  labs(
    title = "GE Matrix for Customer Segments",
    x = "Market Attractiveness (Avg of Income and Age)",
    y = "Business Strength"
  ) +
  theme_minimal()
