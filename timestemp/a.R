data_niko = read.csv("niko.csv", header=FALSE)
data_shaked = read.csv("shaked.csv", header=FALSE)
data_dana = read.csv("dana.csv", header=FALSE)
data_engel = read.csv("engel.csv", header=FALSE)
data = data_engel
names(data) <- c("Sender", "Relative Time")
# convert to hours
data$`Relative Time` <- data$`Relative Time`/60
data$`Relative Time` <- data$`Relative Time`/60

hist(data$`Relative Time`[data$`Relative Time` > 0.25],
     breaks=2000, ylim=c(0,23), xlim=c(0,40),
     ylab="amount", xlab="Relative Time",
     main=paste("Messages Where", "hours", ">", 0.25))

hist(data$`Relative Time`[data$`Relative Time` > 0.5 & data$`Relative Time` < 7],
     breaks=2000, ylab="amount", xlab="Relative Time",
     main=paste("Messages Where", 0.5, "<", "hours", "<", 7))

# short name for interactive use
r <- data$`Relative Time`
length(r) # amount of messages
sum(r <= 0.25) # messages with less than 0.25h delay
hist(r, breaks=4000)
hist(r, breaks=4000, ylim=c(0,5))
hist(r[r > 0.5], breaks=2000)
hist(r[r > 0.5], breaks=2000, xlim=c(0,100))
hist(r[r > 0.5 & r < 7], breaks=60)
sum(r > 0.5 & r < 7)
sum(r >= 7 & r < 24)
