#!/usr/bin/env Rscript
get_data <- function(filename=NULL) {
	if (is.null(filename)) {
		##### parse argv
		# get argv
		argv <- commandArgs(trailingOnly = TRUE)
		# check length argv
		if (!length(argv)) {q(save="no")}
		# make it a file name
		filename <- ifelse(
			endsWith(argv[1], ".csv"),
			argv[1],
			paste(argv[1], ".csv", sep="")
		)
	}
	# load the data
	data <- read.csv(filename, header=FALSE)
	# set appropriate headers
	names(data) <- c("Sender", "Relative Time")
	# convert to hours
	data$`Relative Time` <- data$`Relative Time` / 60^2
	return(data)
}

display_data_stats <- function(r) {
	cat(sprintf("lines                        - %5d (%6.2f%%)\n", length(r)               , length(r)                / length(r) * 100))
	cat(sprintf("lines where        h <= 0.25 - %5d (%6.2f%%)\n", sum(          r <= 0.25), sum(          r <= 0.25) / length(r) * 100))
	cat(sprintf("lines where        h <= 0.5  - %5d (%6.2f%%)\n", sum(          r <= 0.5 ), sum(          r <= 0.5 ) / length(r) * 100))
	cat(sprintf("lines where 0.5 <  h <= 1    - %5d (%6.2f%%)\n", sum(0.5 < r & r <= 1)   , sum(0.5 < r & r <= 1)    / length(r) * 100))
	cat(sprintf("lines where 1   <  h <= 1.5  - %5d (%6.2f%%)\n", sum(1   < r & r <= 1.5) , sum(1   < r & r <= 1.5)  / length(r) * 100))
	cat(sprintf("lines where 1.5 <  h <= 7    - %5d (%6.2f%%)\n", sum(1.5 < r & r <= 7)   , sum(1.5 < r & r <= 7)    / length(r) * 100))
	cat(sprintf("lines where 7   <  h <= 24   - %5d (%6.2f%%)\n", sum(7   < r & r <= 24)  , sum(7   < r & r <= 24)   / length(r) * 100))
	cat(sprintf("lines where 24  <  h         - %5d (%6.2f%%)\n", sum(24  < r)            , sum(24  < r)             / length(r) * 100))
}

plot_histograms <- function(r) {
	hist(r, breaks=4000)
	hist(r, breaks=4000, ylim=c(0,5))
	hist(r[r > 0.5], breaks=2000)
	hist(r[r > 0.5], breaks=2000, xlim=c(0,100))
	hist(r[r > 0.5 & r < 7], breaks=60)

	# hist(data$`Relative Time`[data$`Relative Time` > 0.25],
	#      breaks=2000, ylim=c(0,23), xlim=c(0,40),
	#      ylab="amount", xlab="Relative Time",
	#      main=paste("Messages Where", "hours", ">", 0.25))

	# hist(data$`Relative Time`[data$`Relative Time` > 0.5 & data$`Relative Time` < 7],
	#      breaks=2000, ylab="amount", xlab="Relative Time",
	#      main=paste("Messages Where", 0.5, "<", "hours", "<", 7))
}

main <- function() {
	argv <- commandArgs(trailingOnly = TRUE)
	if (length(argv) & argv[1] == "*") {
		print("shaked")
		display_data_stats(get_data("shaked.csv")$`Relative Time`)
		print("dana")
		display_data_stats(get_data("dana.csv")$`Relative Time`)
		print("niko")
		display_data_stats(get_data("niko.csv")$`Relative Time`)
		print("engel")
		display_data_stats(get_data("engel.csv")$`Relative Time`)
	} else {	
		data <- get_data()
		# short name for interactive use
		r <- data$`Relative Time`
		display_data_stats(r)
	}
}

main()