import java.awt.geom.FlatteningPathIterator;
import java.security.DrbgParameters.NextBytes;
import java.time.Period;
import java.util.Currency;

import javax.imageio.plugins.bmp.BMPImageWriteParam;
import javax.imageio.plugins.tiff.BaselineTIFFTagSet;
import javax.net.ssl.CertPathTrustManagerParameters;
import javax.swing.text.html.InlineView;
import javax.swing.text.html.HTMLDocument.HTMLReader.IsindexAction;
import javax.xml.transform.Templates;

/**
 * 
 */
/**
 * @author zed
 *
 */

public class Link {
	public Link Nexta;
	public int V;
	
	public Link(int v) {
		this.V = v;
	}
	public Link LinkFormatList(int[] vList) {
		Link tmp0 = new Link(0);
		Link tmp1 = new Link(vList[0]);
		tmp0.Nexta = tmp1;
		for (int i = 1; i < vList.length; i++) {
			tmp1.Nexta = new Link(vList[i]);
			tmp1 =tmp1.Nexta;
			
		}
		return tmp0.Nexta;
	}
	
	public Link LinkFormatCirCleList(int[] vList) {
		Link tmp0 = new Link(0);
		Link tmp1 = new Link(vList[0]);
		tmp0.Nexta = tmp1;
		for (int i = 1; i < vList.length; i++) {
			tmp1.Nexta = new Link(vList[i]);
			tmp1 =tmp1.Nexta;		
		}
		tmp1.Nexta =tmp0.Nexta.Nexta.Nexta.Nexta;
		return tmp0.Nexta;
	}
	
	public void appendNext(Link Node) {
		this.Nexta = Node;
	}
	public void printNext() {
		System.out.print(this.V);
		if (this.Nexta == null) {
			return; 
		}
	
		this.Nexta.printNext();
	}
	
	public int getLinkLen(Link head) {
		int n = 0;
		while (head.Nexta != null) {
			head = head.Nexta;
			n++;
		}
		return ++n;
	}

	
	// 反转链表 难 TODO
	public Link revertListdigui(Link head) {   
        //// 边缘条件判断

        if (head == null) {
        	return null;
        }
		if (head.Nexta == null) {
			return head; 
		}
        // 递归调用，翻转第二个节点开始往后的链表

		Link noden =this.revertListdigui(head.Nexta); // 进去的是2 
        // 翻转头节点与第二个节点的指向

		head.Nexta.Nexta = head; // 2 指向1 
        // 此时的 head 节点为尾节点，next 需要指向 NULL

		head.Nexta = null;// 1 指向空
		return noden;	
	}
	
	
	// 反转链表 难 TODO
	public Link reverseListWhile(Link head) { 
		Link prev = null;
		Link curr = head;

        while(curr != null) {
        	Link nxt = curr.Nexta;
            curr.Nexta = prev; // 翻转箭头
            prev = curr; //三人行
            curr = nxt; //三人行
        }

        return prev;
    }
	
	
	//难 TODO 1 2 3 4 5 6链表变 1 3 5 2 4 6
	public Link swapABLink(Link head) {
		Link tepLink = new Link(0); // 设置一个虚拟头结点0
		tepLink.Nexta = head; // 将虚拟头结点指向head，这样方面后面做删除操作
        Link cur = tepLink;
        while(cur.Nexta != null && cur.Nexta.Nexta != null) {
            Link tmp = cur.Nexta; // 记录临时节点 1
            Link tmp1 = cur.Nexta.Nexta.Nexta; // 记录临时节点 3

            cur.Nexta = cur.Nexta.Nexta;    // 步骤一 0指向2
            cur.Nexta.Nexta = tmp;          // 步骤二 2指向1
            cur.Nexta.Nexta.Nexta = tmp1;   // 步骤三 1指向3

            cur = cur.Nexta.Nexta; // cur移动两位，准备下一轮交换 0跳到2
        }
        return tepLink.Nexta;
			
	
	}

	// 难
	public Link swapABLinkgdigui(Link head) {
		 // base case 退出提交
        if(head == null || head.Nexta == null) return head;
        // 获取当前节点的下一个节点
        Link next = head.Nexta;// 取到2
        // 进行递归
        Link newNode = this.swapABLinkgdigui(next.Nexta);// 进去3
        // 这里进行交换
        next.Nexta = head; // 2的下一个是1 
        head.Nexta = newNode; // 1下一个是3

        return next;
	}
	
	// 1 2 3 
	public Link revertdigui(Link head) {
		 // base case 退出提交
       if(head == null || head.Nexta == null) return head;
       // 获取当前节点的下一个节点
       Link next = head.Nexta;// 取到2
       // 进行递归
       Link newNode = this.swapABLinkgdigui(next.Nexta);// 进去3
       // 这里进行交换
       next.Nexta = head; // 2的下一个是1 
       newNode.Nexta = next; // 3下一个是2

       return next;
	}
	
	// 1 2 3 4 5 删除倒数第二个 变 1 2 3 5 双指针经典用法，快慢指针 快指针先走n步，等快指针到尾部，删除慢指针。
	public Link delBackN(Link head,int n) {
		Link fastCurLink = new Link(0);
		Link slowCurLink = new Link(0);
		fastCurLink.Nexta = head;
		slowCurLink.Nexta = head;
		int f =0;
		int sn = 0;
		while (fastCurLink !=null) {
			fastCurLink = fastCurLink.Nexta;
			if (f> n) {
				slowCurLink = slowCurLink.Nexta;
				sn++;
			}
			if (fastCurLink == null) {
				Link tmp = slowCurLink.Nexta.Nexta;
				slowCurLink.Nexta = null;
				slowCurLink.Nexta = tmp;
			}
			f++;
		}		
		return head;		
				
		
	}
	
	// 4 1 8 4 5 和 5 0 1 8 4 5 返回链表相交的点  长的先走多的n步
	public int checkDoubleLinkame(Link head1,Link head2) {
		int sameV= 100;
		int lenMore  = this.getLinkLen(head1) - this.getLinkLen(head2);
		
		Link shortLink = new Link(0);
		Link longLink = new Link(0);
		
		if (lenMore < 0) {
			lenMore = -lenMore;
			longLink = head2;
			shortLink = head1;
		}else {
			longLink = head1;
			shortLink = head2;
		}
		int idx = 1;
		while (longLink.Nexta !=null) {
			longLink = longLink.Nexta;
			if (idx >= lenMore) {
				if (longLink.V == shortLink.V) {
					sameV = longLink.V;
					break;
				}
				shortLink = shortLink.Nexta;
			}
			
			idx++;
		}		
		return sameV;		
				
		
	}

	// 判断环形链表 也是快慢指针 快是慢的二倍 如果有环 一定会相遇
	public int checkCricleLink(Link head) {
		int entenrV= 100;
		Link fastCurLink = new Link(0);
		Link slowCurLink = new Link(0);
		fastCurLink.Nexta = head;
		slowCurLink.Nexta = head;
		int i = 0;
		while (fastCurLink.Nexta.Nexta !=null) {
			fastCurLink = fastCurLink.Nexta.Nexta;
				slowCurLink = slowCurLink.Nexta;
				if (slowCurLink.V == fastCurLink.V) {
					entenrV = fastCurLink.V;
					break;
				}
				if (i>= 100) {
					break;
				}
				i++;
		}		
		return entenrV;			
	}

	public void searchBackN(Link head,int n) {
		Link fastCurLink = head;
		Link slowCurLink = head;
		int slowidx = 0;
		int fastidx = 0;
		while (fastCurLink != null) {
			fastidx++;
			fastCurLink = fastCurLink.Nexta;
		
			if (fastidx > n) {
				slowCurLink = slowCurLink.Nexta;
			}
			
		}
		System.out.println(slowCurLink.V);

	}

	
	public static void main(String[] args) {
        System.out.println(args);
        Link demoLink = new Link(0);
        int[] base = {1,2,3,4,5,6};
        int[] delBackN = {1,2,3,4,5,6};
        int[] same1 = {1,2,3,4,5,6};
        int[] same2 = {7,8,4,5,6};
        int[] circleList = {7,8,4,5,6,1,2,3,9,10,11};
        int[] N = {1,2,3,4,5,6};

        Link baseLink1 = demoLink.LinkFormatList(base);
        Link baseLink2 = demoLink.LinkFormatList(base);
        Link baseLinkN = demoLink.LinkFormatList(N);

        Link delBackNLink  = demoLink.LinkFormatList(delBackN);
        Link same1Link = demoLink.LinkFormatList(same1);
        Link same2Link = demoLink.LinkFormatList(same2);
        Link cirCleLink = demoLink.LinkFormatCirCleList(circleList);
        System.out.println(demoLink.getLinkLen(baseLink1));

        System.out.println("--fanzhuanLinkdigui--");
        demoLink.revertListdigui(baseLink1).printNext();
        System.out.println("\n--fanzhuanLinkWhile--");
        demoLink.reverseListWhile(baseLink2).printNext();
        System.out.println("\n-delBackN--");
        demoLink.delBackN(delBackNLink,3).printNext();;
        System.out.println("\n-checkDoubleLinksame--");
        System.out.println(demoLink.checkDoubleLinkame(same1Link,same2Link));
        System.out.println("\n-checkNoCricleLink--");
        System.out.println(demoLink.checkCricleLink(baseLink1));
        System.out.println("\n-checkCricleLink--");
        System.out.println(demoLink.checkCricleLink(cirCleLink));
        //
        System.out.println("\n-searchBackN--");
        demoLink.searchBackN(baseLinkN,2);
        
    }
    
}

