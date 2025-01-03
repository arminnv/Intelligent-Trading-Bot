import analysis
import back_test
import data_download
import indicators
import order
import plot
import test


def main() -> None:
    back_test.run(120)
    #plot.show_plot()
    #tele.run()

    return


if __name__ == '__main__':
    main()


