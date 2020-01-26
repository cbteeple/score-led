import sys
import yaml


def update(t1, t2):
	thresholds = {
		"thresh_neg": int(t1),
		"thresh_pos" : int(t2)
	}
	with open('thresholds.yaml','w') as f:
		yaml.dump(thresholds,f)


if __name__ == "__main__":
	if len(sys.argv) ==3:
		update(sys.argv[1],sys.argv[2])
	else:
		print("Need to input 2 arguments")
