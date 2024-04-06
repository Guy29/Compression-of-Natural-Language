from stats import *

S = Stats('stats.json')
S.update_all_and_save()
S.compute_similarity_matrix()
S.draw_similarity_heatmap(sort_by='file size', filename='fig_co-compression_file_size.png')
S.draw_similarity_heatmap(sort_by='median', filename='fig_co-compression_median.png')
#S.compute_cocomp_matrix()
#S.draw_cocomp_heatmap(sort_by='file size', filename='fig_cocomp_file_size.png')
#S.draw_cocomp_heatmap(sort_by='median', filename='fig_cocomp_median.png')
S.print_most_least_similar()